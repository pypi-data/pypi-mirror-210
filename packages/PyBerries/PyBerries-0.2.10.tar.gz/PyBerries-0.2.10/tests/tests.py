from os.path import join

import pandas as pd

import pyberries as pyb

path = './tests/'
ds = 'Test_data'
data = pyb.data.DatasetPool(path=path, dsList=ds)
ref_bacteria = pd.read_csv(join(path, ds, f"{ds}_{0}.csv"), sep=';', low_memory=False)
ref_CFP = pd.read_csv(join(path, ds, f"{ds}_{1}.csv"), sep=';', low_memory=False)


class TestDatasetPool():

    def test_data_import(self):
        assert len(data.Bacteria) == len(ref_bacteria)
        assert len(data.CFP_spots) == len(ref_CFP)

    def test_filtering(self):
        data.apply_filters(filters={'Bacteria': 'SpineLength > 3'}, inplace=True)
        assert len(data.Bacteria) == len(ref_bacteria.query('SpineLength > 3'))

    def test_filter_propagation(self):
        data.apply_filters(filters={'Bacteria': 'SpineLength > 3'}, inplace=True)
        assert len(data.CFP_spots) == 42

    def test_add_metadata(self):
        data.add_metadata({'Bacteria': 'DateTime'}, inplace=True)
        assert 'DateTime' in data.Bacteria.columns

    def test_parents(self):
        parents = {'Bacteria': 'Viewfield', 'CFP_spots': 'Bacteria',
                   'mCherry_spots': 'Bacteria', 'YFP_spots': 'Bacteria'}
        assert data._parents == parents

    def test_timeseries(self):
        timeseries_parameters = {'metric': 'ObjectCount', 'col': 'CFPCount', 'timeBin': 1, 'thr': 1}
        data_test = (data
                     .add_metadata({'Bacteria': 'DateTime'})
                     .get_timeseries(object_name='Bacteria', **timeseries_parameters)
                     )
        assert not data_test.Bacteria_timeseries.empty

    def test_add_columns(self):
        data.add_columns(object_name='CFP_spots', metrics='Heatmap', inplace=True)
        assert 'normXpos' in data.CFP_spots.columns

    def test_split_fuse(self):
        data_test = (data
                     .split_column(object_name='Bacteria', col='Indices',
                                   new_cols=['Indices_0', 'Indices_1'], delimiter='-')
                     .fuse_columns(object_name='Bacteria',
                                   columns=['Indices_0', 'Indices_1'], new='Indices_fused', delimiter='-')
                     )
        assert 'Indices_0' in data_test.Bacteria.columns
        assert 'Indices_fused' in data_test.Bacteria.columns

    def test_copy(self):
        data_copy = data.copy()
        data_copy.Bacteria = pd.DataFrame()
        assert len(data.Bacteria) != len(data_copy.Bacteria)


class TestFit():

    def test_Fit(self):
        def model(x, a, b):
            return a*x+b
        test_fit = pyb.data.Fit(data.Bacteria, x='SpineWidth', y='SpineLength', model=model)
        rates = test_fit.get_fit_parameters(param_names=['Slope', 'Offset'])
        assert sum(rates.isna().any()) == 0
