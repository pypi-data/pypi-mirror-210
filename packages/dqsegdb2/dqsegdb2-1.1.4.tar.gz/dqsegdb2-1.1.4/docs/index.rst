.. sectionauthor:: Duncan Macleod <duncan.macleod@ligo.org>

.. toctree::
   :hidden:

   Home <self>

########
DQSEGDB2
########

.. ifconfig:: 'dev' in release

   .. warning::

      You are viewing documentation for a development build of dqsegdb2.
      This version may include unstable code, or breaking changes relative
      the most recent stable release.
      To view the documentation for the latest stable release of dqsegdb2,
      please `click here <../stable/>`_.

.. image:: https://badge.fury.io/py/dqsegdb2.svg
   :target: https://badge.fury.io/py/dqsegdb2
   :alt: dqsegdb2 PyPI release badge
.. image:: https://img.shields.io/pypi/l/dqsegdb2.svg
   :target: https://choosealicense.com/licenses/gpl-3.0/
   :alt: dqsegdb2 license
.. image:: https://zenodo.org/badge/136390328.svg
   :target: https://zenodo.org/badge/latestdoi/136390328
   :alt: dqsegdb2 DOI

``dqsegdb2`` is a simplified Python implementation of the DQSEGDB API as
defined in `LIGO-T1300625 <https://dcc.ligo.org/LIGO-T1300625/public>`__.

.. admonition:: Incomplete API
    :class: info

    This package does not provide a complete implementation of the API
    as defined in LIGO-T1300625, and only supports ``GET`` requests for
    a subset of information available from a DQSEGDB server.
    Any users wishing to make ``POST`` requests should refer to the official
    DQSEGDB Python client available from https://pypi.org/project/dqsegdb/.

    However, ``dqsegdb2`` is light,  with minimal dependencies, so might be
    useful for people only interested in querying for segment information.

============
Installation
============

DQSEGDB2 can be installed with `Pip <https://pip.pypa.io>`__:

.. code-block:: bash

   python -m pip install dqsegdb2

or with `Conda <https://conda.io>`__ from
`conda-forge <https://conda-forge.org>`__:

.. code-block:: bash

   conda install -c conda-forge dqsegdb2

===========
Basic usage
===========

.. code-block:: python

   from dqsegdb2.query import query_segments
   print(query_segments('G1:GEO-SCIENCE:1', 1000000000, 1000001000))

=============
Documentation
=============

The ``dqsegdb.query`` module defines the following functions:

.. automodsumm:: dqsegdb2.query
   :functions-only:
   :toctree: ref
   :caption: dqsegdb2.query

The ``dqsegdb.api`` module defines the following functions:

.. automodsumm:: dqsegdb2.api
   :functions-only:
   :toctree: ref
   :caption: dqsegdb2.api
