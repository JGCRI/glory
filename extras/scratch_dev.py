import glory
import os

# download example data
glory.get_example_data()

# run model ---------------------------------
glory.run_model(config_file=r'C:\WorkSpace\github\glory\example\example_config.yml')

# test separate functions -------------------
config = glory.ConfigReader(config_file=r'C:\WorkSpace\github\glory\example\example_config.yml')

data = glory.DataLoader(config=config,
                        basin_id=83,
                        period=2025,
                        base_period=2020,
                        demand_gcam=None,
                        capacity_gcam=None)

sc = glory.SupplyCurve(config=config,
                       basin_id=83,
                       period=2025,
                       demand_gcam=None,
                       capacity_gcam=None)

# test lp model
lp = glory.lp_model(K=1,
                    Smin=sc.d.storage_min,
                    Ig=sc.d.inflow,
                    Eg=3,
                    f=sc.d.demand_profile,
                    p=sc.d.inflow_profile,
                    z=sc.d.evap_profile,
                    m=sc.d.m,
                    solver='glpk')

glory.diagnostics(config=config, outputs=sc, fig_path=os.path.join(config.output_folder, 'diagnostics'))

#
# # check available solvers for pyomo
# solvers_avail = ['_neos',
#                  '_mock_cbc',
#                  'glpk',
#                  '_glpk_shell',
#                  '_mock_glpk',
#                  '_mock_cplex',
#                  'mpec_nlp',
#                  'mpec_minlp',
#                  'gdpopt',
#                  'gdpopt.gloa',
#                  'gdpopt.lbb',
#                  'gdpopt.loa',
#                  'gdpopt.ric',
#                  'mindtpy',
#                  'mindtpy.oa',
#                  'mindtpy.ecp',
#                  'mindtpy.goa',
#                  'mindtpy.fp',
#                  'multistart',
#                  'scipy.fsolve',
#                  'scipy.root',
#                  'scipy.newton',
#                  'scipy.secant-newton',
#                  'trustregion']
#
#
# import pyomo.environ as pyo
# from itertools import compress
#
# pyomo_solvers_list = pyo.SolverFactory.__dict__['_cls'].keys()
# solvers_filter = []
# for s in pyomo_solvers_list:
#     try:
#         solvers_filter.append(pyo.SolverFactory(s).available())
#     except (Exception) as e:
#         solvers_filter.append(False)
# pyomo_solvers_list = list(compress(pyomo_solvers_list, solvers_filter))
