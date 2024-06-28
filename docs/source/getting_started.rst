Getting Started
===============
This page walks you through the steps of installing ``GLORY`` and running an example.


Installation
------------

Pre-requirements
^^^^^^^^^^^^^^^^

* Before proceeding, ensure that Python is installed (version 3.9 or above). We recommend using Anaconda to set up a virtual environment.

* Additionally, you will need to install the linear programming solver ``glpk``. The recommended method is to use ``conda`` to avoid unexpected issues (refer to the `Pyomo documentation <https://jckantor.github.io/ND-Pyomo-Cookbook/notebooks/01.01-Installing-Pyomo.html#glpk>`_). Make sure to use the same Python environment for all packages.

    * Use ``Conda``

    .. code-block:: bash

        conda install -c conda-forge glpk

    * Use ``Homebrew``

    .. code-block:: bash

        brew install glpk

        # set C linker and include flags so that the pip wheel build can find the headers and library
        LDFLAGS="-L$(brew --prefix glpk)/lib" CFLAGS="-I$(brew --prefix glpk)/include" pip install glpk


Install ``GLORY``
^^^^^^^^^^^^^^^^^

**Option 1:**

Install ``GLORY`` from a command prompt or terminal:

.. code-block:: bash

    pip install glory

**Option 2:**

You can install the development version of ``GLORY`` from GitHub using ``pip`` in a command prompt or terminal:

.. code-block:: bash

    pip install git+https://github.com/JGCRI/glory

This command will automatically install the dependencies. To avoid package version conflicts, consider using a virtual environment.

**Option 3:**

Alternatively, users can clone the ``GLORY`` package from GitHub. Navigate to the desired directory:

.. code-block:: bash

    git clone https://github.com/JGCRI/glory

Then, navigate into the cloned `glory` folder and install ``GLORY`` from a command prompt or terminal :

.. code-block:: bash

    pip install .

Try importing ``GLORY`` to confirm that installation was successful:

.. code-block:: python

    import glory

    glory.__version__


Example Data
------------

Example data and configuration file can be downloaded from Zenodo through this `link <https://zenodo.org/records/10093575>`_, or by using the ``GLORY`` function:

.. code-block:: python

    import glory

    # The example data will be downloaded to the cloned package folder by default.
    glory.get_example_data()

Or, if the user didn't clone the ``GLORY`` package, then specify a desired download location.

.. code-block:: python

    import glory

    # modify example_data_directory to your own desired location
    glory.get_example_data(example_data_directory='path/to/desired/location')

Run
---

With the example data downloaded, a simple configuration can be run:

.. code-block:: python

    import glory
    import os

    # modify the path if downloaded to a different directory
    config_file = os.path.join(glory.DEFAULT_DOWNLOAD_DIR, 'example_config.yml')

    glory.run_model(config_file=config_file)


Check your ``example\outputs`` folder for the results!

Use `GLORY` Modules
-------------------

Instead of running the entire model, one can choose to run certain modules.

To generate a capacity-yield curve and a supply curve with discrete points for a single basin, users can easily instantiate the `glory.SupplyCurve()` object by providing the configuration object. The `glory.SupplyCurve()` will then undertake the process of identifying reservoir storage capacity expansion pathways and calculating the optimized water yield at each storage capacity point. The example below uses California River basin (basin ID is 217) for time step 2020.

.. code-block:: python

    import glory

    # indicate the path to the config file
    config = glory.ConfigReader(config_file=config_file)

    # demand_gcam and capacity_gcam is set to None because the model is not linked with GCAM in this example
    sc = glory.SupplyCurve(config=config,
                           basin_id=217,
                           period=2020,
                           demand_gcam=None,
                           capacity_gcam=None)

    # Check the capacity-yield curve
    sc.capacity_yield

    # check the supply curve
    sc.supply_curve

One can effortlessly apply the `glory.lp_model()` function to execute a linear programming model that determines the optimized water yield for a given reservoir storage capacity. Below is an example with arbitrary numbers. Please note that volumetric units should be consistent across variables.

.. code-block:: python

    import numpy as np

    lp = glory.lp_model(K=1, # set storage capacity as 1 km3
                        Smin=0, # minimum storage
                        Ig=5, # annual inflow in volume
                        Eg=1, # annual reservoir surface evaporation in volume
                        f={i+1: num for i, num in enumerate(np.random.dirichlet(np.ones(12), size=1)[0])}, # dictionary: monthly profile for demand
                        p={i+1: num for i, num in enumerate(np.random.dirichlet(np.ones(12), size=1)[0])}, # dictionary: monthly profile for inflow
                        z={i+1: num for i, num in enumerate(np.random.dirichlet(np.ones(12), size=1)[0])}, # dictionary: monthly profile for reservoir surface evaporation
                        m=0.1, # percentage of water reuse
                        solver='glpk')

    # view the solution
    lp.display()

This will return a `pyomo <https://pyomo.readthedocs.io/en/stable/index.html>`_ object. To display the solution of the linear programming model for each variable, use `lp.display()`.
