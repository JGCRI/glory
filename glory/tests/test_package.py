# Import libraries
import pytest
import glory
import os

def test_get_data():
    """
    test clean_up function
    :return:
    """
    assert os.path.abspath(glory.get_data()) == os.path.abspath(os.path.join(os.getcwd(), 'example'))

def test_read_config():
    """
    test read_config
    :return:
    """
    downloaded_data_path = glory.get_data()
    example_config = os.path.join(downloaded_data_path, 'example_config.yml')
    assert glory.ConfigReader(example_config) == {'path_example_data_set': 'example_data.csv'}

def test_read_data():
    """
    test method
    :return:
    """
    downloaded_data_path = glory.get_data()
    example_config = os.path.join(downloaded_data_path, 'example_config.yml')
    config = glory.ConfigReader(example_config)
    example_key = list(config.keys())[0]
    example_value = os.path.join(downloaded_data_path,list(config.values())[0])
    updated_config = config
    updated_config[example_key] = example_value
    df = (glory.DataLoader(updated_config)).example_data_set
    assert list(df.name)==['a','b','c']
    assert list(df.value) == [1,2,3]

def test_method():
    """
    test method
    :return:
    """
    assert glory.SupplyCurve(2,2) == 4

def test_write_outputs():
    """
    test diagnostics function
    :return:
    """
    assert glory.write_outputs(2,2) == 4

def test_diagnostics():
    """
    test diagnostics function
    :return:
    """
    assert glory.diagnostics(2,2) == 4

def test_clean_up():
    """
    test clean_up function
    :return:
    """
    assert glory.clean_up(2,2) == 4

def test_class():
    """
    test class
    :return:
    """
    # assert glory.SupplyCurve().var == 5
    # assert glory.Pytemplate().config == ''
    # assert glory.Pytemplate().method == 1