Installation
============

Installing earthkit-data
----------------------------

Install **earthkit-data** with python3 (>= 3.8) and **pip** as follows:

.. code-block:: bash

    python3 -m pip install earthkit-data


Installing the binary dependencies
--------------------------------------

eccCodes
+++++++++++

**earthkit-data** depends on the ECMWF *ecCodes* library
that must be installed on the system and accessible as a shared library. The easiest way to install it is to use Conda:

.. code-block:: bash

    conda install eccodes -c conda-forge


On a MacOS it is also available from HomeBrew:

.. code-block:: bash

    brew install eccodes

As an alternative you may install the official source distribution
by following the instructions at
https://software.ecmwf.int/wiki/display/ECC/ecCodes+installation

FDB
+++++

For FDB (Fields DataBase) access FDB5 must be installed in the system. See the `FDB documentation <https://fields-database.readthedocs.io/en/latest/>`_ for details.
