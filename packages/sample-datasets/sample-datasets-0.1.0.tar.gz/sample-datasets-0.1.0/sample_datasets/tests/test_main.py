import pyarrow
import pytest

from sample_datasets import SampleDatasets


def test_inexisting_dataset():
    with pytest.raises(ValueError,
                       match='No dataset named "foo"'):
        SampleDatasets.reader('foo')


def test_geonames_is_pyarrow_table_instance():
    result = SampleDatasets.reader('geonames')
    assert isinstance(result, pyarrow.Table)


def test_geonames_has_correct_size():
    result = SampleDatasets.reader('geonames')
    assert result.num_rows == 250
    assert result.num_columns == 9
