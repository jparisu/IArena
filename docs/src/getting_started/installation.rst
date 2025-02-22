.. _installation:

############
Installation
############

.. _installation_googlecolab:

============
Google Colab
============

Using `Google Colab <https://colab.google>` is the easiest way to get started.
Just add in the first cell of your notebook:

.. code-block:: python

    # Download and install latest version of the package
    !pip install --upgrade git+https://github.com/jparisu/IArena.git

    # Or to download a specific version
    !pip install --upgrade git+https://github.com/jparisu/IArena.git@v0.2

This will install the specific version of the package and make it available in the rest of the cells of your notebook.

===========================
Install in Windows Anaconda
===========================

In order to install the package in Windows Anaconda, the steps are the same as for :ref:`installation_googlecolab`.
The only detail is that ``git`` may not be installed by default in Anaconda.

From a command prompt, you can install it in a conda environment inside Anaconda:

.. code-block:: bash

    conda install git
    pip install --upgrade git+https://github.com/jparisu/IArena.git


===========================
Install with pip
===========================

To install the package with ``pip``, you can use the following command:

.. code-block:: bash

    pip install --upgrade git+https://github.com/jparisu/IArena.git


===========
Coming soon
===========

- Installation from source
