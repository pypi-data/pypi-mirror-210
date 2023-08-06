# DQSEGDB2

[![PyPI version](https://badge.fury.io/py/dqsegdb2.svg)](http://badge.fury.io/py/dqsegdb2)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/dqsegdb2.svg)](https://anaconda.org/conda-forge/dqsegdb2/)
[![License](https://img.shields.io/pypi/l/dqsegdb2.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![DOI](https://zenodo.org/badge/136390328.svg)](https://zenodo.org/badge/latestdoi/136390328)
![Supported Python versions](https://img.shields.io/pypi/pyversions/dqsegdb2.svg)

[![Build status](https://git.ligo.org/duncanmmacleod/dqsegdb2/badges/main/pipeline.svg)](https://git.ligo.org/duncanmmacleod/dqsegdb2/-/pipelines)
![Code coverage](https://git.ligo.org/duncanmmacleod/dqsegdb2/badges/main/coverage.svg)
[![Documentation status](https://readthedocs.org/projects/dqsegdb2/badge/?version=latest)](https://dqsegdb2.readthedocs.io/en/latest/?badge=latest)

DQSEGDB2 is a simplified Python implementation of the DQSEGDB API as defined in
[LIGO-T1300625](https://dcc.ligo.org/LIGO-T1300625).

This package only provides a query interface for `GET` requests, any users
wishing to make `POST` requests should refer to the official `dqsegdb` Python
client available from <https://github.com/ligovirgo/dqsegdb/>.

## Installation

For best results, please install from [conda-forge](https://conda-forge.org/):

```shell
conda install -c conda-forge dqsegdb2
```

On Unix systems, you can also install directly from PyPI:

```shell
pip install dqsegdb2
```

## Basic Usage

```python
from dqsegdb2.query import query_segments
print(query_segments('G1:GEO-SCIENCE:1', 1000000000, 1000001000))
```
