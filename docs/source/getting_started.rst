Getting Started
===============
This page walks you through the steps of installing ``GLORY`` and running an example.


Installation
------------

Pre-requirements
^^^^^^^^^^^^^^^^

- Before proceeding, ensure that Python is installed (version 3.9 or above). We recommend using Anaconda to set up a virtual environment.

- Additionally, you will need to install the linear programming solver ``glpk``. The recommended method is to use ``conda`` to avoid unexpected issues (refer to the `Pyomo documentation <https://jckantor.github.io/ND-Pyomo-Cookbook/notebooks/01.01-Installing-Pyomo.html#glpk>`_). Make sure to use the same Python environment for all packages.

.. code-block:: bash

    conda install -c conda-forge glpk


Install ``GLORY``
^^^^^^^^^^^^^^^^^

**Option 1:**

You can install ``GLORY`` from GitHub using ``pip`` in a command prompt or terminal:

.. code-block:: bash

    pip install git+https://github.com/JGCRI/glory

This command will automatically install the dependencies. To avoid package version conflicts, consider using a virtual environment.

**Option 2:**

Alternatively, users can clone the ``GLORY`` package from GitHub. Navigate to the desired directory:

.. code-block:: bash

    git clone https://github.com/JGCRI/glory

Then, navigate into the cloned `glory` folder and install ``GLORY`` from a command prompt or terminal :

.. code-block:: bash

    pip install

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

    # Or

    # If the user didn't clone the package, then specify a desired download location.
    glory.get_example_data(example_data_directory='path/to/desired/location')


Run
-----------------------------------

With the example data downloaded, a simple configuration can be run:

.. code-block:: python

    import glory
    import os

    # modify the path if downloaded to a different directory
    config_file = os.path.join(glory.default_download_dir, 'example', 'example_config.yml')

    glory.run_model(config_file=config_file)

