import os
import logging


def write_outputs(config, outputs):
    """
    Write outputs

    :param outputs:             class object for outputs
    :return:
    """

    logging.info('Starting function write_outputs.')

    out_path = os.path.join(config.root, config.outputs['output_folder'])

    # write capacity yield curve outputs
    if config.outputs['capacity_yield']:

        write_csv(var='capacity_yield', data=outputs.capacity_yield, period=outputs.period, out_path=out_path)

    # write supply curve outputs
    if config.outputs['supply_curve']:

        write_csv(var='supply_curve', data=outputs.supply_curve, period=outputs.period, out_path=out_path)

    # write capacity trajectory
    # if config.outputs['storage_capacity']:
    #
    #     write_csv(var='storage_capacity', data=outputs.capacity_gcam, period=outputs.period, out_path=out_path)

    logging.info('Function write_outputs completed.')


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

    data.to_csv(
        os.path.join(save_path, '_'.join([var, str(period)]) + '.csv'),
        index=False
    )





