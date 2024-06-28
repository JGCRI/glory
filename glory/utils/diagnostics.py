"""
Module to create diagnostic figures.

@author: Mengqi Zhao (mengqi.zhao@pnnl.gov)

@Project: GLORY v1.0

License:  BSD 3-Clause, see LICENSE and DISCLAIMER files

Copyright (c) 2023, Battelle Memorial Institute

"""

import logging
import os
import matplotlib.pyplot as plt


def diagnostics(config, outputs, fig_path=None):
    """
    Plot capacity yield curve.
    """

    if config.outputs['diagnostics']:

        logging.info('Starting function diagnostics.')

        basin_name = outputs.d.basin_name_std.loc[outputs.d.basin_name_std['basin_id'] == outputs.basin_id, 'basin_name'].iloc[0]

        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 8), constrained_layout=False)

        # plot capacity - yield curve
        ax[0].plot(outputs.capacity_yield['capacity'], outputs.capacity_yield['yield'], color='black', lw=3)
        max_cap, = ax[0].plot(outputs.d.max_capacity, outputs.capacity_yield_interpld(outputs.d.max_capacity),
                              linestyle='None', marker='o', markersize=14, markeredgecolor='black',
                              markerfacecolor='darkorange')
        current_cap, = ax[0].plot(outputs.d.current_capacity, outputs.capacity_yield_interpld(outputs.d.current_capacity),
                                  linestyle='None', marker='o', markersize=10, markeredgecolor='black',
                                  markerfacecolor='lightseagreen')
        ax[0].set_title(str(outputs.basin_id) + ' - ' + basin_name, fontsize=16, fontweight='bold')
        ax[0].legend([max_cap, current_cap], ['max expandable capacity', 'current capacity'], numpoints=1)
        ax[0].set_xlabel('Storage Capacity ($km^3$)', fontsize=14)
        ax[0].set_ylabel('Yield ($km^3/year$)', fontsize=14)
        ax[0].grid()

        # plot supply curve
        ax[1].plot(outputs.supply_curve['available'], outputs.supply_curve['extractioncost'], color='black', lw=3,
                   marker='o', markersize=8, markeredgecolor='black', markerfacecolor='dodgerblue')
        # ax[1].set_title(str(self.basin_id) + ' - ' + basin_name, fontsize=16, fontweight='bold')
        ax[1].set_xlabel('Availability', fontsize=14)
        ax[1].set_ylabel('Price (1975USD/year)', fontsize=14)
        ax[1].grid()

        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        fig.tight_layout()

        fig_path_period = os.path.join(fig_path, str(outputs.period))

        # save figure
        if not os.path.exists(fig_path_period):
            os.makedirs(fig_path_period, exist_ok=True)

        file_path = os.path.join(fig_path_period, str(outputs.basin_id) + ' - ' + basin_name + '.png')
        print(f'Saving diagnostic figure to: {file_path}')
        fig.savefig(file_path)

        logging.info('Function diagnostics completed successfully.')