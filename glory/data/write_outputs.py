"""
Module to write output data.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 3-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import os
import logging
import pandas as pd

def write_outputs(config, outputs):
    """
    Write outputs

    :param outputs:             class object for outputs
    :return:
    """

    logging.info('Starting function write_outputs.')

    out_path = os.path.join(config.root, config.outputs['output_folder'])

    # initialize
    capacity_yield = pd.DataFrame()
    supply_curve = pd.DataFrame()
    lp_solution = pd.DataFrame()

    # outputs is a list of classes. Each class is for a basin
    for out in outputs:

        # get basin_id and basin_name
        basin_id = out.basin_id
        basin_name = out.d.basin_name_std.loc[out.d.basin_name_std['basin_id'] == basin_id, 'basin_name'].values[0]

        # construct capacity yield output for a period
        capacity_yield = pd.concat([capacity_yield, out.capacity_yield], axis=0)
        capacity_yield['basin_id'] = basin_id
        capacity_yield['basin_name'] = basin_name

        # rearrange columns
        capacity_yield = capacity_yield[['basin_id', 'basin_name', 'capacity', 'yield']]

        # construct supply curve for a period
        supply_curve = pd.concat([supply_curve, out.supply_curve], axis=0)

        # construct lp solutions for a period
        lp_solution = pd.concat([lp_solution, out.lp_solution], axis=0)

    period = out.period

    # write capacity yield curve outputs
    if config.outputs['capacity_yield']:

        write_csv(var='capacity_yield', data=capacity_yield, period=period, out_path=out_path)

    # write supply curve outputs
    if config.outputs['supply_curve']:

        write_csv(var='supply_curve', data=supply_curve, period=period, out_path=out_path)

    # write supply curve outputs
    if config.outputs['lp_solution']:

        write_csv(var='lp_solution', data=lp_solution, period=period, out_path=out_path)

    # TODO: write capacity trajectory
    # if config.outputs['storage_capacity']:
    #
    #     write_csv(var='storage_capacity', data=outputs.capacity_gcam, period=outputs.period, out_path=out_path)

    logging.info('write_outputs function completed successfully.')


def write_csv(var, data, period, out_path):
    """
    Write csv outputs

    :param var:                 string for output variable name
    :param data:                df or numpy array for outputs
    :param out_path:            output_path
    :return:
    """

    save_path = os.path.join(out_path, var)
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    file_path = os.path.join(save_path, '_'.join([var, str(period)]) + '.csv')
    print(f'Writing outputs to: {file_path}')
    data.to_csv(file_path, index=False)





