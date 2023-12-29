:notoc:

About
=====

The ``GLORY`` (GLObal Reservoir Yield) model is an open-source Python package designed to optimize water yield for a given reservoir storage capacity while also estimating the economic value of water supply for global river basins. ``GLORY`` was built at the `Joint Global Change Research Institute at the Pacific Northwest National Laboratory <https://www.pnnl.gov/projects/jgcri>`_.

The key functions of ``GLORY`` are as follows:

1) Utilize a linear programming (LP)-based algorithm to maximizes annual water yield by considering a monthly reservoir water balance that accounts for inflow, surface water evaporation, reservoir release, environmental flow, return flow, and spills.

2) Calculate the cost of constructing reservoirs and the prices of water at different reservoir expansion stages across global basins.

The ``GLORY`` model streamlines workflows by integrating information on climate, hydrology, water demand, reservoir exploitable potential, and physiography to estimate the water availability and prices of water supply from reservoirs. ``GLORY`` identify the sub-annual regulation capability and associated investment of reservoirs and establish boundary conditions for basin-level analysis on reservoir management.


.. panels::
    :card: + intro-card text-center
    :column: col-lg-6 col-md-6 col-sm-6 col-xs-12 d-flex


    ---
    :img-top: _static/index_getting_started.svg

    Getting Started
    ^^^^^^^^^^^^^^^

    New to ``GLORY``?  Get familiar with how to install and run ``GLORY``.

    +++

    .. link-button:: getting_started
            :type: ref
            :text: New to GLORY
            :classes: btn-block btn-secondary stretched-link

    ---
    :img-top: _static/index_user_guide.svg

    User Guide
    ^^^^^^^^^^

    The user guide provides in-depth information on the
    key concepts of ``GLORY``.

    +++

    .. link-button:: user_guide
            :type: ref
            :text: GLORY Details
            :classes: btn-block btn-secondary stretched-link

    ---
    :img-top: _static/index_modules.svg

    Modules
    ^^^^^^^^^^^^^

    The reference guide contains a detailed description of
    the ``GLORY`` modules. The reference describes how the methods
    work and which parameters can be used.

    +++

    .. link-button:: modules
            :type: ref
            :text: Modules Reference
            :classes: btn-block btn-secondary stretched-link

    ---
    :img-top: _static/index_contribute.svg

    Contributing to GLORY
    ^^^^^^^^^^^^^^^^^^^^

    Saw a typo in the documentation? Want to improve
    existing functionalities? The contributing guidelines will guide
    you through the process of improving ``GLORY``.

    +++

    .. link-button:: contributing
            :type: ref
            :text: I Want To Contribute
            :classes: btn-block btn-secondary stretched-link

**Date**: |today| **Version**: |version|

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