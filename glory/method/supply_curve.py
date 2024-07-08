"""
Supply curves.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 3-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import numpy as np
import logging
import math
from scipy.interpolate import interp1d
from scipy.interpolate import PchipInterpolator

from glory.data.read_data import DataLoader
from glory.method.lp import *


class SupplyCurve:
    """
    Calculate supply curves based on Capacity-Yield curves from linear programming model

    USAGE:      SupplyCurve(basin_id=id,
                            period=period,
                            demand_gcam=demand_gcam,
                            capacity_gcam=capacity_gcam)

    """

    def __init__(self, config, basin_id, period, demand_gcam, capacity_gcam):

        logging.info(f'Starting function supply_curve for basin {basin_id} in period {period}.')

        self.config = config
        self.basin_id = basin_id
        self.period = period
        self.demand_gcam = demand_gcam
        self.capacity_gcam = capacity_gcam

        self.d = DataLoader(config=self.config,
                            basin_id=basin_id,
                            period=self.period,
                            base_period=self.config.scales['base_period'],
                            demand_gcam=self.demand_gcam,
                            capacity_gcam=self.capacity_gcam)

        # initialized base yield when capacity is 0
        self.lp_solution = None  # LP model solution summary
        self.yield_base = self.run_lp_model(capacity=0, capacity_track=0)

        # initialize output list
        self.output = []
        self.output.append([0, self.yield_base])

        # initialize
        self.init_intv = self.config.parameters['init_segments']  # initial number of intervals for reservoir storage capacity expansion
        self.discount_rate = 0.05  # discount rate for reservoir capital cost
        self.life_time = 60  # lifetime in years
        self.base_price = 1e-04  # starting price for water, $/m3
        self.mantainance = 0.1  # maintanance fee as fraction of reservoir cost

        # parameter
        self.EXCEED_ADJ = 0.8  # multiplier that adjusts variables that goes over maximum allowable values
        self.EXCEED_ADJ_ACTION = False  # binary that shows whether there is an adjustment for separation point for expansion sequence

        self.dx = None  # increment for reservoir storage capacity expansion
        self.inflection_point = None  # inflection point on capacity-yield curve
        self.max_expansion_point = None  # the capacity and yield values for the max expansion point
        self.expansion_unit = None  # storage capacity increments
        self.max_supply = None  # maximum supply
        self.cost_per_m3 = None  # reservoir capital cost in 1975USD/m3

        # discrete capacity-yield curve unconstrained by maximum capacity
        self.capacity_yield_unconstrained = self.get_capacity_yield_unconstrained()

        # interpolatable capacity-yield curve
        self.capacity_yield_interpld = interp1d(self.capacity_yield_unconstrained['capacity'],
                                                self.capacity_yield_unconstrained['yield'],
                                                bounds_error=False,
                                                fill_value=max(self.capacity_yield_unconstrained['yield']))

        # get capacity yield curve (constrained by maximum capacity)
        self.capacity_yield = self.get_capacity_yield_constrained()

        # storage capacity expansion sequence
        self.expansion_seq = self.get_expansion_sequence()

        # yield increment sequence based on storage capacity expansion path
        self.yield_increment_seq = self.get_yield_gain_sequence()

        # cost per unit expansion
        self.cost = self.cost_per_expansion()

        # price
        self.price = self.levelized_cost()

        # supply curve
        self.supply_curve = self.construct_supply_curve()

        # maxsubresource
        self.maxsubresource = self.construct_maxsubresource()

        logging.info('Function supply_curve completed successfully.')

    def get_reservoir_evap(self, capacity_track):
        """
        calculate reservoir surface area based on current storage capacity.
        Calculate reservoir ET in km3/year based on the new storage capacity in each basin.

        :param capacity_track:          list for reservoir capacity expansion track

        :return:
        """

        if isinstance(capacity_track, float) or isinstance(capacity_track, int):
            df_ini = pd.DataFrame({capacity_track}, columns=['capacity'])
        elif isinstance(capacity_track, list):
            df_ini = pd.DataFrame(capacity_track, columns=['capacity'])
        elif capacity_track is None:
            raise TypeError('Capacity Track can not be None.')

        start = df_ini.iloc[0, 0]
        end = df_ini.iloc[-1, 0]

        if end - start > self.d.expan_incr:
            df = pd.DataFrame(np.append(np.arange(start, end, self.d.expan_incr), end), columns=['capacity'])
        else:
            df = df_ini.copy()

        # calculate the changes in capacity
        df['increase'] = df['capacity'].diff()
        df.loc[0, 'increase'] = df.loc[0, 'capacity']

        # get b and c for Volume-Area Correlation V = c * A^b
        b = self.d.reservoir['b'].iloc[0]
        c = self.d.reservoir['c'].iloc[0]

        # calculate corresponding area for each increase in capacity
        df['area'] = (df['increase'] / c) ** (1 / b)

        # calculate et volume
        df['evap'] = df['area'] * self.d.evap_depth

        # calculate total evaporation from total capacity
        evap_vol = sum(df['evap'])

        if evap_vol > self.d.inflow:
            evap_vol = self.d.inflow * self.EXCEED_ADJ

        return evap_vol

    def run_lp_model(self, capacity, capacity_track):
        """
        Run LP model.

        :param capacity:                float for target capacity
        :param capacity_track:          list for tracking capacity at each iteration

        :return:                        value for optimized yield
        """

        evap_vol = self.get_reservoir_evap(capacity_track=capacity_track)

        model = lp_model(K=capacity, Smin=self.d.storage_min, Ig=self.d.inflow, Eg=evap_vol,
                         f=self.d.demand_profile, p=self.d.inflow_profile, z=self.d.evap_profile, m=self.d.m,
                         solver=self.config.lp['solver'])

        # optimal value
        val = model.obj()

        # solution outputs
        solution = lp_solution(model=model, K=capacity, basin_id=self.basin_id, period=self.period)

        # concat solutions from different K values
        if self.lp_solution is None:
            self.lp_solution = solution
        else:
            self.lp_solution = pd.concat([self.lp_solution, solution])

        return val

    def set_dx(self):
        """
        The algorithm of choosing dx in this section is to prevent the LP model running over 500 iterations,
        or not enough iterations (<50).
        However, another thing to notice is that the inflection point when reaches mean annual inflow.
        This requires we make sure there are enough iteration before the inflection point (20 or more).
        The algorithm is used to detect if the yield value with K = dx is less than 0.05 of Ig or
        Y0+0.05(Ig-Y0) if Y0 != 0, dx is reduced to 1/2 until dx satisfies the condition.

        :return:                none
        """

        # rough estimate of dx using max capacity potential and initial number of intervals
        dx_coarse = self.d.max_capacity / self.init_intv

        # calculate the iterations based on max capacity potential and the expansion increment
        iteration = int(math.ceil(self.d.max_capacity / self.d.expan_incr))

        if (iteration > 500) or (iteration < 50):
            self.dx = dx_coarse
        else:
            self.dx = self.d.expan_incr

        # initialize initial yield from first incremental capacity expansion
        yield_dx = self.run_lp_model(capacity=self.dx, capacity_track=self.dx)

        # deduce dx so that it is small enough where the increase in yield value is less than 5% of the difference
        # between average annual inflow and base yield
        n = 0
        while yield_dx > (self.yield_base + 0.05 * (self.d.inflow - self.yield_base)):
            self.dx = self.dx / 2
            yield_dx = self.run_lp_model(capacity=self.dx, capacity_track=self.dx)
            n += 1

        # increase dx so that the initial incremental yield from base yield if capacity expand dx is large enough
        # to make half of the intervals before inflection point
        n = 0
        try:
            while (self.d.inflow - self.yield_base) / (yield_dx - self.yield_base) > self.init_intv / 2:
                # print('Calculating Basin - ', self.basin_id, ', current dx is ', self.dx)
                self.dx = self.dx * 2
                yield_dx = self.run_lp_model(capacity=self.dx, capacity_track=self.dx)
                n += 1
        except ZeroDivisionError as err:
            pass

    def get_capacity_yield_unconstrained(self):
        """
        Calculate capacity yield curve.

        :return:                dataframe
        """
        # set dx for the curve before inflection point
        self.set_dx()

        # calculate capacity-yield curve before reaching inflection point
        i = 0
        capacity_cum = 0
        capacity_track = [capacity_cum]
        while self.output[i][1] < (self.yield_base + 0.95 * (self.d.inflow - self.yield_base)):
            capacity_cum += self.dx
            capacity_track.append(capacity_cum)
            yield_cum = self.run_lp_model(capacity=capacity_cum, capacity_track=capacity_track)

            if yield_cum - self.output[i][1] > 0:
                self.output.append([capacity_cum, yield_cum])
                i += 1
            else:
                capacity_track.remove(capacity_track[-1])
                capacity_cum = capacity_track[-1]
                break

        # average slope from the last 5 points from the inflection point
        slope = (np.diff(list(list(zip(*self.output[-5:]))[1])) / np.diff(list(list(zip(*self.output[-5:]))[0]))).mean()

        # determine the dx for the part approaching inflection point to be enough to capture the curve details
        while self.output[i][1] - self.output[i - 1][1] > 0:
            if slope < 1.5:
                capacity_cum += min(self.dx / 2, self.d.expan_incr)
                capacity_track.append(capacity_cum)
            else:
                capacity_cum += min(self.dx / 10, self.d.expan_incr)
                capacity_track.append(capacity_cum)

            yield_cum = self.run_lp_model(capacity=capacity_cum, capacity_track=capacity_track)

            if yield_cum > self.output[i][1]:
                self.output.append([capacity_cum, yield_cum])
                i += 1
            else:
                capacity_track.remove(capacity_track[-1])
                capacity_cum = capacity_track[-1]
                logging.info(f'Basin {self.basin_id} : {i} iterations')
                break

        # inflection point is the point on the capacity-yield curve where yield will NOT increase with capacity
        self.inflection_point = pd.DataFrame({'capacity': [self.output[-1][0]], 'yield': [self.output[-1][1]]})

        if self.output[-1][0] < self.d.max_capacity:
            # if maximum expandable capacity is higher than the inflection point
            # calculate the yield at max expandable capacity
            # reservoir construction after inflection point is still by capacity_cum size
            capacity_extend = np.append(
                np.arange(self.output[-1][0] + capacity_cum, self.d.max_capacity, capacity_cum),
                self.d.max_capacity)
            capacity_track.extend(capacity_extend.tolist())
            yield_cum = self.run_lp_model(capacity=self.d.max_capacity, capacity_track=capacity_track)

            self.max_expansion_point = pd.DataFrame({'capacity': [self.d.max_capacity],
                                                     'yield': [yield_cum],
                                                     'exceed_inflection': 'yes'})

        return pd.DataFrame(self.output, columns=['capacity', 'yield'])

    def get_capacity_yield_constrained(self):
        """
        Constrain the capacity yield curve by max capacity.

        :return:
        """

        # # if the inflection point goes beyond max capacity, keep the curve to max capacity
        # capacity_yield_constrained = self.capacity_yield_unconstrained.loc[
        #     self.capacity_yield_unconstrained['capacity'] < self.d.max_capacity]
        #
        # # if the inflection point goes beyond max capacity, keep the curve after max capacity
        # capacity_yield_exceed = self.capacity_yield_unconstrained.loc[
        #     self.capacity_yield_unconstrained['capacity'] > self.d.max_capacity]

        # get maximum yield constrained by maximum capacity
        # This value may be adjusted if max cap > inflection point
        max_expansion_yield_adj = self.capacity_yield_interpld(self.d.max_capacity)[()]

        max_cap_yield = pd.DataFrame({'capacity': [self.d.max_capacity], 'yield': [max_expansion_yield_adj]})

        if self.max_expansion_point is None:
            self.max_expansion_point = pd.DataFrame({'capacity': [self.d.max_capacity],
                                                     'yield': [max_expansion_yield_adj],
                                                     'exceed_inflection': 'no'})

        # append constrained max point
        capacity_yield_constrained = pd.concat([self.capacity_yield_unconstrained, max_cap_yield], ignore_index=True). \
            sort_values(by=['capacity', 'yield'], ignore_index=True).drop_duplicates()

        capacity_yield_constrained.reset_index(drop=True, inplace=True)

        return capacity_yield_constrained

    def get_expansion_sequence(self):
        """
        Determine the evenly spaced intervals for incremental storage capacity and get capacity expansion sequence.

        :return:                1D array
        """
        # find the first index when it just reaches the highest yield
        index_inflection = self.capacity_yield[self.capacity_yield['yield'] == max(self.capacity_yield.iloc[:, 1])].index[0]

        # Method 1 ============
        # # determine numbers of intervals
        # num = max(5, int(math.ceil(self.capacity_yield.iloc[index_inflection, 0] / self.d.expan_incr)))
        #
        # # capacity expansion increments
        # self.expansion_unit = self.capacity_yield.iloc[index_inflection, 0] / num
        #
        # # set the sequence of storage capacity expansion
        # expansion = np.linspace(0, self.capacity_yield.iloc[index_inflection, 0], num)

        # Method 2 ============
        # set expansion unit the same as defined expan_incr
        self.expansion_unit = self.d.expan_incr

        # capacity at the inflection point
        cap_inflection = self.capacity_yield.iloc[index_inflection, 0]

        # initial array with interval of expan_incr
        expansion = np.arange(0,
                              cap_inflection,
                              self.expansion_unit)

        # append the last point if the value is not extremely small
        if (cap_inflection - expansion[-1]) / self.expansion_unit > 0.5:
            expansion = np.append(expansion, cap_inflection)

        return expansion

    def get_yield_gain_sequence(self):
        """
        Calculate yield increments sequence based on reservoir storage capacity expansion.
        two segments of yield increment sequences: (1) before max capacity and (2) after max capacity

        :return:                1D array
        """

        # determine the break point to separate expansion sequence
        # this is to avoid the situation when max capacity exceed inflection point, because
        # 1. it does not make sense to keep expanding capacity when no more water can be provided
        # 2. the expansion sequence after separation point means using other facilities rather than reservoirs,
        #    and the costs will be higher to create enough curvature for supply curves
        if self.inflection_point.loc[0, 'capacity'] < self.d.max_capacity:
            separate_point = self.inflection_point.loc[0, 'capacity'] * self.EXCEED_ADJ
            self.EXCEED_ADJ_ACTION = True
        else:
            separate_point = self.d.max_capacity

        expansion_seq_pre = self.expansion_seq[self.expansion_seq <= separate_point]
        expansion_seq_after = self.expansion_seq[self.expansion_seq > separate_point]

        yield_gain_pre = self.capacity_yield_interpld(expansion_seq_pre[1:]) - \
                         self.capacity_yield_interpld(expansion_seq_pre[:-1])

        if len(expansion_seq_after) == 0:
            yield_gain_after = None
        else:
            expansion_seq_after = np.insert(expansion_seq_after, 0, expansion_seq_pre[-1])
            yield_gain_after = self.capacity_yield_interpld(expansion_seq_after[1:]) - \
                               self.capacity_yield_interpld(expansion_seq_after[:-1])

        yield_gain = [yield_gain_pre, yield_gain_after]

        return yield_gain

    def cost_per_expansion(self):
        """
        Calculate the cost in 1975 USD per unit reservoir storage capacity expansion

        :return:                float in million 1975$
        """
        # cost = 15.375 * pow(Kexp, 0.3995) # million AUD$ For watersupply reservoirs, unit GL (Petheram et al., 2019)
        # convert from GL to unit km3 (Petheram et al., 2019)
        # convert from AUD to USD for 2016: 1 USD = 1.345 AUD in 2016
        # (source: https://data.worldbank.org/indicator/PA.NUS.FCRF?end=2020&locations=AU&start=2006)
        # convert 2016 USD to 1975 USD = 101.049/28.511 = 3.544: Deflators 1975 (28.511) to 2016 (101.049)
        # (source: World Bank https://data.worldbank.org/indicator/NY.GDP.DEFL.ZS?locations=US&view=chart)

        # val = 242.8371 * pow(self.expansion_unit, 0.3995) / 1.345 / 3.544

        # convert capacity from km3 to million m3
        cap_mcm = self.expansion_unit * 1e3

        # slope
        x = self.d.slope

        # calculate estimated cost based on storage cose - slope relationships
        # this is normalized cost in cost/m3, the value still need to be converted to 1975 USD
        if 0 <= cap_mcm < 25:
            val = 0.0197 * x ** 2 + 0.0538 * x + 0.5818
        elif 25 <= cap_mcm < 49:
            val = 0.0295 * x ** 2 - 0.0044 * x + 0.4456
        elif 49 <= cap_mcm < 74:
            val = 0.034 * x ** 2 - 0.031 * x + 0.3982
        elif 74 <= cap_mcm < 123:
            val = 0.037 * x ** 2 - 0.0521 * x + 0.3655
        elif 123 <= cap_mcm < 247:
            val = 0.0372 * x ** 2 - 0.0607 * x + 0.3094
        elif 247 <= cap_mcm < 493:
            val = 0.0368 * x ** 2 - 0.0671 * x + 0.2633
        elif 493 <= cap_mcm < 1233:
            val = 0.0372 * x ** 2 - 0.0607 * x + 0.3094
        elif 1233 <= cap_mcm < 2467:
            val = 0.0362 * x ** 2 - 0.0824 * x + 0.1895
        elif 2467 <= cap_mcm < 4934:
            val = 0.0368 * x ** 2 - 0.0671 * x + 0.2633
        elif 4934 <= cap_mcm < 12335:
            val = 0.0334 * x ** 2 - 0.0868 * x + 0.1427
        elif 12335 <= cap_mcm:
            val = 0.0314 * x ** 2 - 0.0896 * x + 0.1111

        # assuming the average unit cost of reservoirs based on
        # Keller, A., R. Sakthivadivel and D. Seckler. 2000. “Water Scarcity and the Role of Storage in Development.”
        # estimate mean of small and medium project (~ 0.13 * 4 = 0.52 1998$/m3 ),
        # and mean of large storage projects (~ 0.11 * 4 = 0.44 1998$/m3) and take mean between two
        # Table 5 is in 1998 US dollars and need to be converted to 1975 USD
        # https://data.worldbank.org/indicator/FP.CPI.TOTL?locations=US
        mean_global_reservoir_cost = (0.52 + 0.44) / 2

        convert_1998_to_1975_usd = 24.7 / 74.8

        # final unit is million 1975$ per expansion unit
        cost_per_expansion = \
                                         (1 + self.mantainance) * val * self.expansion_unit * 10 ** 9 * mean_global_reservoir_cost * convert_1998_to_1975_usd / 10 ** 6

        # calculate cost per m3
        self.cost_per_m3 = np.array([[self.basin_id, cost_per_expansion * 10e6 / (self.expansion_unit * 10 ** 9)]])

        return cost_per_expansion

    def levelized_cost(self):
        """
        Calculate levelized cost of storage capacity (LCOSC) as 1975 USD per unit water yield.

        :return:                1D numpy array
        """
        if self.EXCEED_ADJ_ACTION:
            cost_arr = np.array([self.cost, self.cost * 10])
        else:
            cost_arr = np.array([self.cost, self.cost * 5])

        with np.errstate(divide='ignore'):
            price_increment_pre = np.where(self.yield_increment_seq[0] == 0,
                                           0,
                                           (cost_arr[0] * 10 ** 6 * self.discount_rate /
                                            (1 - pow(1 + self.discount_rate, -self.life_time))) / (
                                                   self.yield_increment_seq[0] * 10 ** 9))
            if self.yield_increment_seq[1] is not None:
                price_increment_after = np.where(self.yield_increment_seq[1] == 0,
                                                 0,
                                                 (cost_arr[1] * 10 ** 6 * self.discount_rate /
                                                  (1 - pow(1 + self.discount_rate, -self.life_time))) / (
                                                         self.yield_increment_seq[1] * 10 ** 9))
                price_increment = np.concatenate((price_increment_pre, price_increment_after), axis=None)
            else:
                price_increment = price_increment_pre

            # when there is no reservoir, water costs $0
            price_increment = np.insert(price_increment, 0, self.base_price)

            price = np.cumsum(price_increment, dtype=float)

        return price

    def get_20_point_supply_curve(self, supply_curve_raw):
        """
        This is to get 20-point sequence of yields with monotonic cubic spline.

        :param supply_curve_raw:            dataframe for raw supply curve without supply sequence spacing and smoothing

        :return:
        """
        # monotonic cubic spline interpolation
        supply_curve_interpld = PchipInterpolator(supply_curve_raw['supply'], supply_curve_raw['price'])

        seq_sample = np.linspace(0, self.max_supply, num=100, endpoint=True)

        # calculate 2nd order derivative
        dx = seq_sample[1] - seq_sample[0]
        y = supply_curve_interpld(seq_sample)
        dydx = np.gradient(y, dx)

        # mean of the gradient
        grad_mean = np.mean(dydx)

        # inflection index
        index_inflection = np.where(dydx < grad_mean)[0][-1]

        # keep the high gradient part of the sequence
        index_back = np.where(dydx > grad_mean)[0]
        index_back = index_back[index_back > index_inflection]
        if len(index_back) or (index_back[-1] - index_back[0]) > 10:
            space = max(math.ceil(len(index_back) / 10), math.ceil((index_back[-1] - index_back[0]) / 10))
            index_back = np.unique(np.append(np.arange(index_back[0], index_back[-1] + 1, space), index_back[-1]))

        # the first two front indexes need to be at lease 0 and 1e-5, to have enough curvature for GCAM
        price_seq_front = supply_curve_interpld(seq_sample[0:index_inflection])
        price_index = np.where(price_seq_front > self.base_price)[0]

        if len(price_index) == 0:
            price_index = np.where(price_seq_front > self.base_price / 10)[0]

        # calculate space of the flat part of the sequence
        space = max(math.ceil((price_index[-1] - price_index[0]) / (17 - len(index_back))), 1)

        # get flat part sequence index
        index_front = np.arange(price_index[0], price_index[-1] + 1, space)
        index_front = np.insert(index_front, 0, 0)

        # check if total length of front and back index is smaller than 18
        i = 1
        length = len(index_front) + len(index_back)
        while len(index_front) + len(index_back) < 18:
            space = math.ceil((price_index[0] / 3) / (18 - length))
            index_front = np.append(index_front, price_index[0] - space * i)
            i += 1

        # full index
        index = np.sort(np.concatenate((index_front, index_back), axis=None))

        # sequence
        seq = seq_sample[index]

        # interpolate price in supply curve
        supply_curve = pd.DataFrame({'supply': seq, 'price': supply_curve_interpld(seq)})

        # smooth the curve with rolling mean, which makes curve 20 point in most cases
        window = 5
        if window > 0:
            supply_curve_forward = supply_curve.rolling(window=window, min_periods=1).mean()
            supply_curve_backward = supply_curve[::-1].rolling(window=window, min_periods=1).mean()[::-1]
            supply_curve = pd.concat([supply_curve_forward, supply_curve_backward]).round(decimals=6)
            supply_curve = supply_curve.drop_duplicates().sort_values(by=['supply', 'price'], ignore_index=True)

        supply_curve_interpld = PchipInterpolator(supply_curve['supply'], supply_curve['price'])

        j = 2
        while len(supply_curve) > 20:
            supply_curve.drop(supply_curve.index[-j], axis=0, inplace=True)
            j += 2

        while len(supply_curve) < 20:
            seq_append = seq_sample[np.where(dydx < grad_mean)[0][-i]]
            temp = pd.DataFrame({'supply': [seq_append], 'price': [supply_curve_interpld(seq_append)[()]]})
            supply_curve = pd.concat([supply_curve, temp]).sort_values(by=['supply', 'price'], ignore_index=True)
            i += 2

        supply_curve.reset_index(drop=True, inplace=True)

        return supply_curve

    def get_20_even_point_supply_curve(self, supply_curve_raw):
        """
        This is to get 20 evenly spaced point on supply sequence to get the curve.

        :param supply_curve_raw:
        :return:
        """

        supply_curve = supply_curve_raw

        # get the 20 evenly spaced points for x axis (supply)
        supply_seq = np.linspace(supply_curve.loc[0, 'supply'], self.max_supply, num=20, endpoint=True)

        # smooth the curve with rolling mean, which makes curve 20 point in most cases
        window = 5
        if window > 0:
            supply_curve_forward = supply_curve.rolling(window=window, min_periods=1).mean()
            supply_curve_backward = supply_curve[::-1].rolling(window=window, min_periods=1).mean()[::-1]
            supply_curve = pd.concat([supply_curve_forward, supply_curve_backward]).round(decimals=6)
            supply_curve = supply_curve.drop_duplicates().sort_values(by=['supply', 'price'], ignore_index=True)

        # Interpolate smoothed supply curve
        supply_curve_interpld = PchipInterpolator(supply_curve['supply'], supply_curve['price'])

        # 20 points supply curve
        supply_curve_20pt = pd.DataFrame({'supply': supply_seq, 'price': supply_curve_interpld(supply_seq)})

        return supply_curve_20pt

    def construct_supply_curve(self):
        """
        Construct supply curve.

        :return:                2D numpy array
        """
        # supply for all expansion points
        supply = self.capacity_yield_interpld(
            np.unique(np.concatenate((self.expansion_seq[:-1], self.expansion_seq[1:]))))

        # get maximum supply
        self.max_supply = supply[-1]

        # combine supply and price in to 2D array
        supply_curve_lp = np.vstack((supply, self.price)).T

        # starting point for supply curve
        supply_curve_min = np.array([0, 0], ndmin=2)

        # defined the entire curve
        supply_curve = pd.DataFrame(np.concatenate((supply_curve_min, supply_curve_lp), axis=0),
                                    columns=['supply', 'price'])

        # 20 points supply curve
        supply_curve_20pt = self.get_20_point_supply_curve(supply_curve_raw=supply_curve)
        # supply_curve_20pt = self.get_20_even_point_supply_curve(supply_curve_raw=supply_curve)

        # update max supply since the digit is limited to 6
        self.max_supply = supply_curve_20pt.iloc[19, 0]

        # Append 20 points supply curve to data frame
        gcam_basin_name = \
            self.d.basin_name_std.loc[self.d.basin_name_std['basin_id'] == self.basin_id, ['gcam_basin_name']].iloc[
                0, 0]
        supply_curve_append = pd.DataFrame({'resource': gcam_basin_name + '_water withdrawals',
                                            'grade': ['grade{}'.format(i) for i in range(1, 21)],
                                            'available': supply_curve_20pt['supply'] / self.max_supply,
                                            'extractioncost': supply_curve_20pt['price']})

        # change to numpy
        # supply_curve_array = supply_curve_append.to_numpy()

        return supply_curve_append

    def construct_maxsubresource(self):
        """
        Construct new maxSubResource dataframe based on the max supply constrained by the max capacity.

        :return:
        """

        # extract region that has the largest portion of the basin
        region = self.d.basin_name_std.loc[self.d.basin_name_std['basin_id'] == self.basin_id, 'region'].iloc[0]

        # renewresource
        resource = self.d.basin_name_std.loc[
                       self.d.basin_name_std['basin_id'] == self.basin_id, 'gcam_basin_name'].iloc[
                       0] + '_water withdrawals'

        maxsubresource = pd.DataFrame({'region': [region],
                                       'resource': [resource],
                                       'subresource': ['runoff'],
                                       'year': [self.period],
                                       'maxSubResource': [self.max_supply]})

        # change to numpy
        # maxsubresource_array = maxsubresource.to_numpy()

        return maxsubresource

