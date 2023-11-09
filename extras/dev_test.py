import glory
import os

config = glory.ConfigReader(config_file=r'C:\WorkSpace\github\glory\example\example_config.yml')

data = glory.DataLoader(config=config,
                        period=2025,
                        base_period=2020,
                        demand_gcam=None,
                        capacity_gcam=None)

sc = glory.SupplyCurve(config=config,
                       period=2025,
                       demand_gcam=None,
                       capacity_gcam=None)

glory.diagnostics(config=config, outputs=sc, fig_path=os.path.join(config.output_folder, 'diagnostics'))

