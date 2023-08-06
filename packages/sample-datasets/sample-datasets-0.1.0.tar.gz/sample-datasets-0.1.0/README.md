# Sample Datasets

Provide sample datasets with the standard I/O interface for Python
dataframes.

## Installation

```sh
pip install sample-datasets
```

## Usage

```python
import pandas

pandas.load_io_plugins()

df = pandas.read_sample_dataset(name="geonames")
```
