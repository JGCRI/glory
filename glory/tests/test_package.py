# Import libraries
import pytest
import glory
import os

# download example data
glory.get_example_data()
downloaded_data_path = os.path.abspath(glory.default_download_dir)
dir_output = os.path.join(downloaded_data_path, 'outputs')

# config file
config_file = os.path.join(downloaded_data_path, 'example_config.yml')


# modify the config file root directory
def replace_line(filename, line_number, text):
    """
    replace lines in a file.

    :filename:       string for path to the file
    :line_number:    integer for the line number to replace
    :text:           string for replacement text
    """

    with open(filename) as file:
        lines = file.readlines()
    lines[line_number - 1] = text

    with open(filename, 'w') as file:
        for line in lines:
            file.write(line)


replace_line(
    filename=config_file,
    line_number=2,
    text=f'root: {downloaded_data_path}\n'
)



# read config
config = glory.ConfigReader(config_file)

# read data
data = glory.DataLoader(config=config,
                        basin_id=83,
                        period=2025,
                        base_period=2020,
                        demand_gcam=None,
                        capacity_gcam=None)

# supply curve
sc = glory.SupplyCurve(config=config,
                       basin_id=83,
                       period=2025,
                       demand_gcam=None,
                       capacity_gcam=None)

# lp model
lp = glory.lp_model(K=1,
                    Smin=sc.d.storage_min,
                    Ig=sc.d.inflow,
                    Eg=3,
                    f=sc.d.demand_profile,
                    p=sc.d.inflow_profile,
                    z=sc.d.evap_profile,
                    m=sc.d.m,
                    solver='glpk')

# run model
glory.run_model(config_file=config_file)

# --------------------------------------------
# Test Modules
# --------------------------------------------


def test_read_config():
    """
    test read_config
    """

    basin_to_country = os.path.abspath(config.reference_files['basin_to_country_mapping'])

    assert basin_to_country == os.path.abspath(os.path.join(downloaded_data_path,  'inputs', 'basin_to_country_mapping.csv'))


def test_read_data():
    """
    test read_data function
    """

    assert data.basin_name_std.shape == (235, 4)


def test_lp_model():
    """
    test lp_model function
    """

    assert lp.obj() >= 0


def test_lp_solution():
    """
    test lp solution
    """

    assert list(sc.lp_solution.columns.values) == ['basin_id', 'period', 'month', 'storage_capacity', 'inflow', 'evaporation',
                                                   'release', 'environmental_flow', 'return_flow', 'spill', 'storage']


def test_supply_curve():
    """
    test supply curve output
    """

    assert len(sc.supply_curve) == 20


def test_write_outputs():
    """
    test write_outputs function
    """

    dir_capacity_yield = os.path.abspath(os.path.join(dir_output, 'capacity_yield', 'capacity_yield_2030.csv'))
    dir_supply_curve = os.path.abspath(os.path.join(dir_output, 'supply_curve', 'supply_curve_2030.csv'))
    dir_lp_solution = os.path.abspath(os.path.join(dir_output, 'lp_solution', 'lp_solution_2030.csv'))

    assert os.path.exists(dir_capacity_yield)
    assert os.path.exists(dir_supply_curve)
    assert os.path.exists(dir_lp_solution)


def test_diagnostics():
    """
    test diagnostics function
    """

    dir_diag_plot = os.path.abspath(os.path.join(dir_output, 'diagnostics', '2030', '83 - Guadalquivir.png'))

    assert os.path.exists(dir_diag_plot)


# --------------------------------------------
# Test Warnings
# --------------------------------------------

def test_warning():
    """
    test warning messages in the functions
    """

    with pytest.raises(FileNotFoundError):
        glory.ConfigReader(os.path.join(downloaded_data_path, 'example_config_test.yml'))

    with pytest.raises(TypeError):
        glory.ConfigReader(os.path.join(downloaded_data_path, 'inputs', 'basin_to_country_mapping.csv'))
