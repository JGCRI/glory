"""
Linear programming model.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 2-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import pandas as pd
from pyomo.environ import *


def lp_model(K, Smin, Ig, Eg, f, p, z, m, solver='glpk'):
    """
    Construct Capacity-Yield Curve with Linear Programming Model.

    :param K:       float for reservoir storage capacity
    :param Smin:    int for minimum required active storage for the reservoir
    :param Ig:      float for annual average inflow (over GCAM 5 year time period) to reference reservoirs that has q total storage capacity of Kgref
    :param Eg:      float for annual average evaporation (over GCAM 5 year time period) from reference reservoirs that has q total storage capacity of Kgref
    :param f:       dictionary for demand fraction profile
    :param p:       dictionary for inflow fraction profile
    :param z:       dictionary for evaporation fraction profile
    :param m:       float for fraction of flow released from distributed reservoirs

    :return:        array for capacity - yield curve
    """

    # Linear Programming Model for Water Storage
    model = ConcreteModel()

    # Set model time periods
    TimePeriods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    LastTimePeriod = 12

    # Define variables
    model.Y = Var(within=NonNegativeReals, initialize=0)
    model.S = Var(TimePeriods, within=NonNegativeReals)
    model.R = Var(TimePeriods, within=NonNegativeReals)
    model.X = Var(TimePeriods, within=NonNegativeReals)
    model.RF = Var(TimePeriods, within=NonNegativeReals)

    # Define parameters
    model.K = Param(initialize=K, within=NonNegativeReals)

    model.f = Param(TimePeriods, initialize=f, within=PercentFraction)
    model.p = Param(TimePeriods, initialize=p, within=PercentFraction)
    model.z = Param(TimePeriods, initialize=z, within=PercentFraction)

    # Define inflow
    def Inflow_init(model, t):
        return max(model.p[t] * (Ig), 0)

    model.I = Param(TimePeriods, initialize=Inflow_init)

    # Define evaporation
    def Evap_init(model, t):
        return max(model.z[t] * (Eg), 0)

    model.E = Param(TimePeriods, rule=Evap_init)

    # Define environmental flow
    def EnvFlow_init(model, t):
        return 0.1 * model.I[t]

    model.EF = Param(TimePeriods, rule=EnvFlow_init)

    # Constraints ----------------------------------------------
    # Define mass balance constraint
    def Mass_rule(model, t):
        if t == LastTimePeriod:
            return model.S[1] == model.S[t] + model.I[t] - model.E[t] - model.EF[t] - model.R[t] + model.RF[t] - \
                   model.X[t]
        else:
            return model.S[t + 1] == model.S[t] + model.I[t] - model.E[t] - model.EF[t] - model.R[t] + model.RF[t] - \
                   model.X[t]

    model.Mass = Constraint(TimePeriods, rule=Mass_rule)

    # Define storage constraint
    def Storage_rule(model, t):
        return (Smin, model.S[t], model.K)

    model.Storage = Constraint(TimePeriods, rule=Storage_rule)

    # Define release constraint
    def Release_rule(model, t):
        return model.R[t] >= model.f[t] * model.Y

    model.Release = Constraint(TimePeriods, rule=Release_rule)

    # Define return flow constraint
    def ReturnFlow_rule(model, t):
        return model.RF[t] == m * (model.R[t] + model.EF[t])

    model.ReturnFlow = Constraint(TimePeriods, rule=ReturnFlow_rule)

    # Objective ----------------------------------------------
    model.obj = Objective(expr=model.Y, sense=maximize)

    # Solve the problem
    opt = SolverFactory(solver)
    opt.solve(model, tee=False)

    return model

def lp_solution(model, K, basin_id, period):
    """

    :param model:               pyomo model object
    :param K:                   float for storage capacity
    :param basin_id:            int for basin id
    :param period:              int for model period
    :return:                    data frame for all the water balance variables
    """

    # retrieve values of optimal model variables
    I = [value(model.I[key]) for key in model.I]
    E = [value(model.E[key]) for key in model.E]
    R = [value(model.R[key]) for key in model.R]
    EF = [value(model.EF[key]) for key in model.EF]
    RF = [value(model.RF[key]) for key in model.RF]
    X = [value(model.X[key]) for key in model.X]
    S = [value(model.S[key]) for key in model.S]

    # create data frame
    df = pd.DataFrame(
        {'basin_id': basin_id,
         'period': period,
         'month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
         'storage_capacity': K,
         'inflow': I,
         'evaporation': E,
         'release': R,
         'environmental_flow': EF,
         'return_flow': RF,
         'spill': X,
         'storage': S}
    )

    return df