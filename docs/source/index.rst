:notoc:

About
=====

The ``GLORY`` (GLObal Reservoir Yield) model is an open-source Python package designed to optimize water yield for a given reservoir storage capacity while also estimating the economic value of water supply for global river basins. ``GLORY`` was built at the `Joint Global Change Research Institute at the Pacific Northwest National Laboratory <https://www.pnnl.gov/projects/jgcri>`_.

The key functions of ``GLORY`` are as follows:

1) Utilize a linear programming (LP)-based algorithm to maximizes annual water yield by considering a monthly reservoir water balance that accounts for inflow, surface water evaporation, reservoir release, environmental flow, return flow, and spills.

2) Calculate the cost of constructing reservoirs and the prices of water at different reservoir expansion stages across global basins.

The ``GLORY`` model streamlines workflows by integrating information on climate, hydrology, water demand, reservoir exploitable potential, and physiography to estimate the water availability and prices of water supply from reservoirs. ``GLORY`` identify the sub-annual regulation capability and associated investment of reservoirs and establish boundary conditions for basin-level analysis on reservoir management.


.. grid:: 1 2 2 2
    :gutter: 2
    :class-container: class-container

    .. grid-item-card:: Getting Started
        :columns: 12 6 6 6
        :class-card: sd-text-center sd-fs-5 sd-rounded-3
        :class-header: sd-py-5
        :class-title: sd-py-2
        :class-body: sd-py-2
        :link: getting_started
        :link-type: doc

        :material-regular:`double_arrow;6em`
        ^^^

        New to ``GLORY``? Get familiar with how to install and run ``GLORY``.

        .. button-ref:: getting_started
            :ref-type: doc
            :shadow:
            :color: secondary
            :click-parent:
            :expand:
            :align: center

            New to GLORY


    .. grid-item-card:: User Guide
        :columns: 12 6 6 6
        :class-card: sd-text-center sd-fs-5 sd-rounded-3
        :class-header: sd-py-5
        :class-title: sd-py-2
        :class-body: sd-py-2
        :link: user_guide
        :link-type: doc

        :material-regular:`menu_book;6em`
        ^^^

        The user guide provides in-depth information on the key concepts of ``GLORY``.

        .. button-ref:: user_guide
            :ref-type: doc
            :shadow:
            :color: secondary
            :click-parent:
            :expand:
            :align: center

            GLORY Details


    .. grid-item-card:: Modules
        :columns: 12 6 6 6
        :class-card: sd-text-center sd-fs-5 sd-rounded-3
        :class-header: sd-py-5
        :class-title: sd-py-2
        :class-body: sd-py-2
        :link: modules
        :link-type: doc

        :material-regular:`blur_on;6em`
        ^^^

        The reference describes the functions and parameters of the ``GLORY`` modules.

        .. button-ref:: modules
            :ref-type: doc
            :shadow:
            :color: secondary
            :click-parent:
            :expand:
            :align: center

            Module References


    .. grid-item-card:: Contributing to GLORY
        :columns: 12 6 6 6
        :class-card: sd-text-center sd-fs-5 sd-rounded-3
        :class-header: sd-py-5
        :class-title: sd-py-2
        :class-body: sd-py-2
        :link: contributing
        :link-type: doc

        :material-regular:`tips_and_updates;6em`
        ^^^

        The contributing pages guides you through the process of improving ``GLORY``.

        .. button-ref:: contributing
            :ref-type: doc
            :shadow:
            :color: secondary
            :click-parent:
            :expand:
            :align: center

            I Want To Contribute


**Date**: |today|    |    **Version**: |version|

**Useful links**:
`Github Repository <https://github.com/JGCRI/glory>`_ |
`Issues & Ideas <https://github.com/JGCRI/glory/issues>`_

.. toctree::
   :maxdepth: 2
   :hidden:

   getting_started
   user_guide
   modules
   contributing
   license
   acknowledgement