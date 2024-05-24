"""
Linear programming model.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 3-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import pandas as pd
import pyomo.environ as pyo


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
    model = pyo.ConcreteModel()

    # Set model time periods
    TimePeriods = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    LastTimePeriod = 12

    # Define variables
    model.Y = pyo.Var(within=pyo.NonNegativeReals, initialize=0)
    model.S = pyo.Var(TimePeriods, within=pyo.NonNegativeReals)
    model.R = pyo.Var(TimePeriods, within=pyo.NonNegativeReals)
    model.X = pyo.Var(TimePeriods, within=pyo.NonNegativeReals)
    model.RF = pyo.Var(TimePeriods, within=pyo.NonNegativeReals)

    # Define parameters
    model.K = pyo.Param(initialize=K, within=pyo.NonNegativeReals)

    model.f = pyo.Param(TimePeriods, initialize=f, within=pyo.PercentFraction)
    model.p = pyo.Param(TimePeriods, initialize=p, within=pyo.PercentFraction)
    model.z = pyo.Param(TimePeriods, initialize=z, within=pyo.PercentFraction)

    # Define inflow
    def Inflow_init(model, t):
        return max(model.p[t] * (Ig), 0)

    model.I = pyo.Param(TimePeriods, initialize=Inflow_init, within=pyo.NonNegativeReals)

    # Define evaporation
    def Evap_init(model, t):
        return max(model.z[t] * (Eg), 0)

    model.E = pyo.Param(TimePeriods, rule=Evap_init, within=pyo.NonNegativeReals)

    # Define environmental flow
    def EnvFlow_init(model, t):
        return 0.1 * model.I[t]

    model.EF = pyo.Param(TimePeriods, rule=EnvFlow_init, within=pyo.NonNegativeReals)

    # Constraints ----------------------------------------------
    # Define mass balance constraint
    def Mass_rule(model, t):
        if t == LastTimePeriod:
            return model.S[1] == model.S[t] + model.I[t] - model.E[t] - model.EF[t] - model.R[t] + model.RF[t] - \
                   model.X[t]
        else:
            return model.S[t + 1] == model.S[t] + model.I[t] - model.E[t] - model.EF[t] - model.R[t] + model.RF[t] - \
                   model.X[t]

    model.Mass = pyo.Constraint(TimePeriods, rule=Mass_rule)

    # Define storage constraint
    def Storage_rule(model, t):
        return (Smin, model.S[t], model.K)

    model.Storage = pyo.Constraint(TimePeriods, rule=Storage_rule)

    # Define release constraint
    def Release_rule(model, t):
        return model.R[t] >= model.f[t] * model.Y

    model.Release = pyo.Constraint(TimePeriods, rule=Release_rule)

    # Define return flow constraint
    def ReturnFlow_rule(model, t):
        return model.RF[t] == m * (model.R[t] + model.EF[t])

    model.ReturnFlow = pyo.Constraint(TimePeriods, rule=ReturnFlow_rule)

    # Objective ----------------------------------------------
    model.obj = pyo.Objective(expr=model.Y, sense=pyo.maximize)

    # Solve the problem
    opt = pyo.SolverFactory(solver)
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
    I = [pyo.value(model.I[key]) for key in model.I]
    E = [pyo.value(model.E[key]) for key in model.E]
    R = [pyo.value(model.R[key]) for key in model.R]
    EF = [pyo.value(model.EF[key]) for key in model.EF]
    RF = [pyo.value(model.RF[key]) for key in model.RF]
    X = [pyo.value(model.X[key]) for key in model.X]
    S = [pyo.value(model.S[key]) for key in model.S]

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