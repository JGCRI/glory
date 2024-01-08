"""
Module to load input data files.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import logging
import os
import pandas as pd


class DataLoader:
    """
    Load Data
    """

    global capacity_gcam_pre

    def __init__(self, config, basin_id, period, base_period=2020, demand_gcam=None, capacity_gcam=None):
        """
        Initialization

        :param basin_id:            integer for basin id to select
        :param period:              integer for period (year)
        :param base_period:         integer for base year
        :param demand_gcam:         dataframe for GCAM sovled demand
        :param capacity_gcam:       dataframe for storage capacity based on GCAM solved runoff demand
        """

        logging.info(f'Starting function read_data for basin {basin_id}.')

        self.basin_id = basin_id
        self.period = period
        self.base_period = base_period
        self.demand_gcam = demand_gcam
        self.capacity_gcam = capacity_gcam

        self.climate = self.load_data(config.input_files['climate'])
        self.profile = self.load_data(config.input_files['monthly_profile'])
        self.demand_hist = self.load_data(config.input_files['sectoral_demand'])
        self.reservoir = self.load_data(config.input_files['reservoir'])
        self.slope = self.load_data(config.input_files['slope'])['slope'].iloc[0]
        self.basin_name_std = self.load_basin_mapping(f_basin_country=config.reference_files['basin_to_country_mapping'],
                                                      f_basin_region=config.reference_files['basin_to_region_mapping'],
                                                      header_num=7)

        self.inflow = self.climate.loc[self.climate['period'] == self.period, 'runoff_km3'].iloc[0]
        self.evap_depth = self.climate.loc[self.climate['period'] == self.period, 'evaporation_km'].iloc[0]
        self.res_area = self.reservoir['nonhydro_area_km2'].iloc[0]

        self.inflow_profile = dict(zip(self.profile.loc[self.profile['period'] == self.period, 'month'],
                                       self.profile.loc[self.profile['period'] == self.period, 'inflow']))
        self.evap_profile = dict(zip(self.profile.loc[self.profile['period'] == self.period, 'month'],
                                     self.profile.loc[self.profile['period'] == self.period, 'evaporation']))
        self.demand_profile = self.get_demand_profile()

        # capacity values
        self.no_expansion = False
        self.max_capacity = self.get_max_capacity()
        self.current_capacity = self.get_current_capacity()

        # expected incremental size for reservoir storage capacity expansion
        self.expan_incr = self.reservoir['mean_cap_km3'].iloc[0]

        # define constant
        self.storage_min = 0
        self.m = 0.1

        logging.info('Function read_data completed successfully.')

    def load_data(self, fn, header_num=0):
        """
        Load data from a CSV file to pandas dataframe.

        :param fn:              string for name of file to load
        :param header_num:      integer for number of lines in file to skip, if text or csv file

        :return:                pandas dataframe
        """
        if not os.path.isfile(fn):
            raise IOError("Error: File does not exist:", fn)

        # for CSV files
        elif fn.endswith('.csv'):
            df = pd.read_csv(fn, skiprows=header_num)
            df = df.loc[df['basin_id'] == self.basin_id]

        else:
            raise RuntimeError("File {} has unrecognized extension".format(fn))

        return df

    def load_gcam_demand(self):
        """
        Load and Format data extract from GCAM using gcamwrapper. The data should be for 235 basins, 6 demand sectors,
        and a single time period.

        :return:                dataframe for sectoral annual demand for selected basin
        """

        if self.demand_gcam is not None:

            df = self.demand_gcam

            # convert objects columns to string
            df = df[['sector', 'subsector', 'year', 'physical-demand']]. \
                rename(columns={'subsector': 'gcam_basin_name', 'physical-demand': 'value'})
            df[['sector', 'gcam_basin_name']] = df[['sector', 'gcam_basin_name']].astype('string', errors='raise')

            # format water withdrawal extracted from GCAM using gcamwrapper
            df['sector'] = df['sector'].str.split(pat='_', expand=True).astype('string', errors='raise').iloc[:, 2]

            # replace demand sector names
            rep = {'an': 'livestock', 'elec': 'electric', 'ind': 'industry',
                   'irr': 'irrigation', 'muni': 'domestic', 'pri': 'mining'}
            df = df.replace({'sector': rep})

            # add standard basin id and basin name
            df = df.merge(self.basin_name_std, how='left', on='gcam_basin_name')

            # filter to selected basin
            df = df.loc[df['basin_id'] == self.basin_id]

            # aggregate demand for each sector within each basin
            grp = df.groupby(['basin_id', 'gcam_basin_name', 'sector', 'year'], as_index=False).sum()

            # rename column 'value'
            grp = grp.rename(columns={'value': 'demand_km3'})

        else:
            grp = None

        return grp

    @staticmethod
    def load_basin_mapping(f_basin_country, f_basin_region, header_num=7):
        """
        Mapping different formats of basin names.

        :param fn:              string for full file path
        :param header_num:      integer for numbers of rows to skip until the header

        :return:                dataframe
        """

        # load basin mapping data
        df_basin = pd.read_csv(f_basin_country, skiprows=header_num)
        df_region = pd.read_csv(f_basin_region)

        # select relevant columns and rename
        df_basin = df_basin.loc[:, ['GCAM_basin_ID', 'Basin_long_name', 'GLU_name']]

        df_basin = df_basin.rename(columns={'GCAM_basin_ID': 'basin_id',
                                            'Basin_long_name': 'basin_name',
                                            'GLU_name': 'gcam_basin_name'})

        # convert from object to string or int
        df_basin[['basin_name', 'gcam_basin_name']] = df_basin[['basin_name', 'gcam_basin_name']].astype('string', errors='raise')
        df_basin['basin_id'] = df_basin['basin_id'].astype('int32', errors='raise')

        # join region name
        df = pd.merge(df_basin, df_region, how='left', on=['gcam_basin_name'])

        return df

    def get_demand_profile(self):
        """
        Calculate total demand profile with historical sectoral profile and sectoral demand.

        :param data_type:           string for input demand data. 'hist' or 'gcam'

        :return:                    dictionary
        """

        if self.period <= self.base_period:
            # get historical demand
            df_demand = self.demand_hist[['sector', 'demand_km3']]

        elif self.period > self.base_period:
            if self.load_gcam_demand() is None:
                df_demand = self.demand_hist[['sector', 'demand_km3']]
            else:
                if self.load_gcam_demand()['demand_km3'].sum() == 0:
                    print('Basin: ', self.basin_id, ' has a sum of 0 demand from all sectors. Replace demand profile with historical profile.')
                    df_demand = self.demand_hist[['sector', 'demand_km3']]
                else:
                    # reformat gcam withdrawal
                    df_demand = self.load_gcam_demand()[['sector', 'demand_km3']]

        # only keep sectoral demand profiles and melt
        df = self.profile.loc[self.profile['period'] == self.period].copy()
        df = df.drop(['basin_id', 'basin_name', 'period', 'evaporation', 'inflow'], axis=1). \
            melt(id_vars=['month']).rename(columns={'variable': 'sector'})

        # merge annual demand and sectoral demand profiles
        df = pd.merge(df, df_demand, how='left', on=['sector'])

        # calculate demand amount for each demand sector
        df['demand_sector'] = df['value'] * df['demand_km3']

        # calculate total monthly demand by aggregating all demand sectors
        df = df.groupby('month', as_index=False).sum()

        # calculate profile
        df['profile'] = df['demand_sector'] / df['demand_km3']

        # construct dictionary for month and demand profile
        dict_out = dict(zip(df['month'], df['profile']))

        return dict_out

    def get_current_capacity(self):
        """
        calculate if there will be expansion on storage capacity.

        :return:                float value for storage capacity
        """

        if self.period <= self.base_period:
            # existing storage capacity
            val = self.reservoir['nonhydro_cap_km3'].iloc[0]

        if self.capacity_gcam is not None:
            if self.period == self.base_period + 5:

                val = max(self.reservoir['nonhydro_cap_km3'].iloc[0],
                          self.capacity_gcam.loc[self.capacity_gcam['basin_id'] == self.basin_id, 'capacity_gcam'].values[0])
            else:
                # if gcam solved capacity is larger than previous capacity, then expand
                capacity_gcam_pre_basin = capacity_gcam_pre.loc[capacity_gcam_pre['basin_id'] == self.basin_id, 'capacity_gcam'].values[0]
                capacity_gcam_basin = self.capacity_gcam.loc[self.capacity_gcam['basin_id'] == self.basin_id, 'capacity_gcam'].values[0]
                if capacity_gcam_basin > capacity_gcam_pre_basin:
                    val = capacity_gcam_basin
                else:
                    val = capacity_gcam_pre_basin
        else:
            val = self.reservoir['nonhydro_cap_km3'].iloc[0]

        return val

    def get_max_capacity(self):
        """
        Adjust maximum storage capacity value only if the basin have no expandable capacity.
        Max storage capacity input data for some basins is already adjusted based on the historical storage capacity.

        :return:            float64
        """
        val = self.reservoir['expan_cap_km3'].iloc[0]

        # adjust max storage cap to mean annual runoff both max and current capacities are 0
        if val == 0:
            val = 0.01 * self.climate.loc[self.climate['period'] == self.period, 'runoff_km3'].iloc[0]

        return val
