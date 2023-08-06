import importlib


class SampleDatasets:
    @staticmethod
    def reader(name):
        """
        Read the sample dataset specified by name.

        Parameters
        ----------
        name : str
            Name of the dataset to load.

        Returns
        -------
        dataframe
            A dataframe object of the library being used with the sample
            data.
        """
        try:
            mod = importlib.import_module(f'sample_datasets._{name}')
        except ImportError:
            raise ValueError(f'No dataset named "{name}"')
        else:
            return mod.data
