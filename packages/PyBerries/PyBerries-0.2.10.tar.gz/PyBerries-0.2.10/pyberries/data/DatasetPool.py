import copy
import json
from os import listdir
from os.path import exists, join
from warnings import warn

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import display

import pyberries as pyb

from .util import arg_to_list, dict_val_to_list, set_to_several_objects, _get_histogram


class DatasetPool():

    def __init__(self,
                 path,
                 dsList,
                 groups=[],
                 metadata={},
                 filters={},
                 preprocessing={}
                 ):

        path = arg_to_list(path)
        dsList = arg_to_list(dsList)
        preprocessing = dict_val_to_list(preprocessing)

        self.path = path
        self.dsList = dsList
        self._parents = dict()

        for i, ds in enumerate(dsList):
            ds_path = path[0] if len(path) == 1 else path[i]
            assert exists(ds_path), f'Bacmman folder not found: {ds_path}'
            assert exists(join(ds_path, ds)), \
                f'Dataset {ds} not found.\n\
                    Maybe looking for {" or ".join([x for x in listdir(ds_path) if x.startswith(ds[0:6])])}?'
            assert (len(groups) >= len(dsList)) or not groups, \
                'If groups are provided, one group should be defined per dataset'

            # Load configuration
            cf = join(ds_path, ds, f"{ds}_config.json")
            with open(cf, errors='ignore') as f:
                conf = json.load(f)
                object_class_names = [c["name"] for c in conf["structures"]["list"]]
                object_parents = [c["segmentationParent"] for c in conf["structures"]["list"]]

            # Add Viewfield object if measurement table is available
            if exists(join(ds_path, ds, f"{ds}_{-1}.csv")):
                object_class_names.insert(0, 'Viewfield')
                object_parents.insert(0, [])
                start_table = -1
            else:
                start_table = 0

            # Load data tables
            k = 0
            for j, obj in enumerate(object_class_names, start_table):
                df_in = pd.read_csv(join(ds_path, ds, f"{ds}_{j}.csv"), sep=';', low_memory=False)
                df_in['Dataset'] = ds
                df_in['Group'] = groups[i] if groups else i
                df_in[['Dataset', 'Group']] = df_in[['Dataset', 'Group']].astype('category')
                if obj in preprocessing.keys():
                    if len(preprocessing[obj]) == 1:
                        df_in = df_in.transform(preprocessing[obj][0])
                    elif len(preprocessing[obj]) > 1:
                        assert len(preprocessing[obj]) == len(self.dsList), \
                            'If multiple pre-processings are provided, there should be one per dataset'
                        if preprocessing[obj][i]:
                            df_in = df_in.transform(preprocessing[obj][i])
                df = df_in if obj not in self.__dict__.keys() else pd.concat([self[obj], df_in], axis=0)
                setattr(self, obj, df)
                if object_parents[k]:
                    self._parents[obj] = object_class_names[object_parents[k][0]-start_table]
                else:
                    self._parents[obj] = 'Viewfield'
                k += 1
            print(f'Dataset {ds}: loaded objects {object_class_names}')
        self.objects = list(self._parents.keys())
        for obj in self.objects:
            self[obj].reset_index(drop=True, inplace=True)

        self = (self
                .add_metadata(metadata)
                .apply_filters(filters)
                )

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

    def copy(self):
        new_dp = copy.deepcopy(self)
        return new_dp

    def describe(self, agg, object_name: str = None, include: str = 'all'):
        include = arg_to_list(include)
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = self.objects
        for obj in objects:
            df = self[obj]
            if include != ['all']:
                df = df.filter(items=include + ['Dataset', 'Group'])
                if not [item for item in list(df.columns) + ['All'] if item in include]:
                    df = pd.DataFrame()
            print(f'{obj}')
            if df.empty:
                print('No data')
            else:
                df1 = (df
                       .groupby('Dataset', sort=False)
                       .agg(nObjects=('Dataset', 'count'))
                       )
                df2 = (df
                       .loc[:, (~df.columns
                                .isin(['Position', 'PositionIdx', 'Indices', 'Frame', 'Idx', 'Time', 'Group']))]
                       .groupby('Dataset', sort=False)
                       .agg(agg, numeric_only=True)
                       )
                if isinstance(agg, list):
                    df2.columns = df2.columns.map(' ('.join) + ')'
                df3 = df[['Group', 'Dataset']].drop_duplicates().set_index('Dataset')
                df_out = df3.join([df1, df2])
                display(df_out)

    def has_na(self, object_name=None):
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = self.objects
        for obj in objects:
            df = (self[obj]
                  .loc[:, (~self[obj].columns
                           .isin(['Position', 'PositionIdx', 'Indices', 'Frame', 'Idx', 'Time', 'Group', 'Dataset']))]
                  )
            if not df.empty:
                print(f'{obj}')
                display(df.isna().sum())

    def dropna(self, object_name=None, inplace=False, **kwargs):
        dp = self if inplace else self.copy()
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = dp.objects
        for obj in objects:
            if not dp[obj].empty:
                dp[obj] = dp[obj].dropna(**kwargs)
        if not inplace:
            return dp

    def fillna(self, object_name=None, col=None, inplace=False, **kwargs):
        dp = self if inplace else self.copy()
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = dp.objects
        for obj in objects:
            if not dp[obj].empty:
                if col:
                    dp[obj][col] = dp[obj][col].fillna(**kwargs)
                else:
                    dp[obj] = dp[obj].fillna(**kwargs)
        if not inplace:
            return dp

    def set_type(self, object_name=None, type_dict={}, inplace=False):
        dp = self if inplace else self.copy()
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = dp.objects
        for obj in objects:
            obj_type = {key: value for key, value in type_dict.items() if key in dp[obj].columns}
            if not dp[obj].empty:
                dp[obj] = dp[obj].astype(obj_type)
        if not inplace:
            return dp

    def drop_duplicates(self, object_name=None, inplace=False, **kwargs):
        dp = self if inplace else self.copy()
        if object_name:
            objects = arg_to_list(object_name)
        else:
            objects = dp.objects
        for obj in objects:
            if not dp[obj].empty:
                dp[obj] = dp[obj].drop_duplicates(**kwargs)
        if not inplace:
            return dp

    def head(self, nlines: int = 5):
        for obj in self.objects:
            print(f'{obj}')
            if self[obj].empty:
                print('No data')
            else:
                display(self[obj].head(nlines))

    def add_metadata(self, metadata, inplace=False):
        dp = self if inplace else self.copy()
        metadata = set_to_several_objects(metadata, dp.objects)
        metadata = dict_val_to_list(metadata)
        for obj in metadata.keys():
            if not dp[obj].empty:
                df = dp[obj]
                for var in metadata[obj]:
                    df[var.replace(' ', '_')] = 0
                    if var == 'DateTime':
                        df['TimeDelta'] = 0
                        df['Time_min'] = 0
                    for i, ds in enumerate(dp.dsList):
                        ds_path = dp.path[0] if len(dp.path) == 1 else dp.path[i]
                        for pos in df.loc[df['Dataset'] == ds].Position.unique():
                            if exists(join(ds_path, ds, 'SourceImageMetadata', f'{pos}_c0.txt')):
                                metadata_filename = f'{pos}_c0.txt'
                            else:
                                metadata_filename = f'{pos}_c0_t0.txt'
                            with open(join(ds_path, ds, 'SourceImageMetadata', metadata_filename)) as f:
                                value = next((line for line in f if var in line), None)
                                # Add metadata value to the current dataset and position
                                df.loc[(df['Position'] == pos) &
                                       (df['Dataset'] == ds), var.replace(' ', '_')] = value.split('=')[-1][:-1]
                        if 'DateTime' in df.columns:
                            df.loc[df['Dataset'] == ds] = (df.loc[df['Dataset'] == ds]
                                                           .assign(DateTime=lambda df:
                                                                   pd.to_datetime(df.DateTime,
                                                                                  format='%Y%m%d %H:%M:%S.%f'),
                                                                   TimeDelta=lambda df:
                                                                   df.DateTime - df.DateTime.iloc[0],
                                                                   Time_min=lambda df:
                                                                   df.TimeDelta.dt.total_seconds().div(60)
                                                                   )
                                                           )
                dp[obj] = df
        if not inplace:
            return dp

    def apply_filters(self, filters, inplace=False):
        dp = self if inplace else self.copy()
        filters = set_to_several_objects(filters, dp.objects)
        filters = dict_val_to_list(filters)
        for obj, filter in filters.items():
            if len(filter) == 1:
                setattr(dp, obj, dp[obj].query(filter[0]))
            elif len(filter) > 1:
                assert len(filter) == len(dp.dsList), \
                    'If multiple filters are provided, there should be one per dataset'
                df = pd.DataFrame()
                i = 0
                for _, data in dp[obj].groupby('Dataset', sort=False):
                    if filter[i]:
                        df = pd.concat([df, data.query(filter[i])], axis=0)
                    else:
                        df = pd.concat([df, data], axis=0)
                    i += 1
            # Propagate filters to children (if any)
            for child, parent in dp._parents.items():
                if parent == obj:
                    dp.propagate_filters(parent, child, inplace=True)
        if not inplace:
            return dp

    def propagate_filters(self, parent: str, child: str, inplace=False):
        dp = self if inplace else self.copy()
        dp.get_parent_indices(obj=child, inplace=True)
        dp[child] = (dp[child]
                     .merge(dp[parent][['Dataset', 'PositionIdx', 'Indices']],
                            suffixes=(None, '_tmp'),
                            left_on=['Dataset', 'PositionIdx', 'ParentIndices'],
                            right_on=['Dataset', 'PositionIdx', 'Indices'])
                     .transform(lambda df: df.loc[:, ~df.columns.str.contains('_tmp')])
                     )
        if not inplace:
            return dp

    def rename_object(self, rename: dict, inplace=False):
        dp = self if inplace else self.copy()
        for old_name, new_name in rename.items():
            if new_name in dp.objects:
                dp[new_name] = (pd.concat([dp[new_name], dp[old_name]], axis=0)
                                  .reset_index(drop=True, inplace=True))
            else:
                dp[new_name] = dp[old_name]
                dp._parents[new_name] = dp._parents[old_name]
            for child, parent in dp._parents.items():
                if parent == old_name:
                    dp._parents[child] = new_name
            delattr(dp, old_name)
            del dp._parents[old_name]
            dp.objects = list(dp._parents.keys())
        if not inplace:
            return dp

    def get_parent_indices(self, obj: str, indices: str = 'Indices', newcol: str = 'ParentIndices', inplace=False):
        dp = self if inplace else self.copy()
        dp[obj][newcol] = (dp[obj][indices]
                           .str.split('-', expand=True)
                           .iloc[:, :-1]
                           .agg('-'.join, axis=1)
                           )
        if not inplace:
            return dp

    def get_idx(self, obj: str, idx: int = 0, indices: str = 'Indices', newcol: str = 'ParentIdx', inplace=False):
        dp = self if inplace else self.copy()
        dp[obj][newcol] = (dp[obj][indices]
                           .str.split('-', expand=True)
                           .iloc[:, idx]
                           .astype('int64')
                           )
        if not inplace:
            return dp

    def fuse_columns(self, object_name: str = None, columns: list = [], new: str = 'new_col',
                     delimiter: str = '-', inplace=False):
        dp = self if inplace else self.copy()
        if not object_name:
            object_name = dp.objects
        else:
            object_name = arg_to_list(object_name)
        for obj in object_name:
            dp[obj][new] = (dp[obj][columns]
                            .astype('str')
                            .agg(delimiter.join, axis=1)
                            )
        if not inplace:
            return dp

    def split_column(self, col: str, new_cols: list, delimiter: str, object_name: str = None, inplace=False):
        dp = self if inplace else self.copy()
        if not object_name:
            object_name = dp.objects
        else:
            object_name = arg_to_list(object_name)
        for obj in object_name:
            dp[obj][new_cols] = (dp[obj][col]
                                 .str.split(delimiter, expand=True)
                                 )
        if not inplace:
            return dp

    def normalise(self, object_name: str, col: str = '', normalise_by: str = '', new_col: str = '', inplace=False):
        dp = self if inplace else self.copy()
        if new_col in dp[object_name].columns:
            dp[object_name].drop(columns=new_col, inplace=True)
        if new_col:
            dp[object_name] = (dp[object_name]
                               .assign(new_tmp=lambda df: df[col] / df[normalise_by])
                               .rename(columns={'new_tmp': new_col})
                               )
        else:
            dp[object_name] = (dp[object_name]
                               .assign(new_tmp=lambda df: df[col] / df[normalise_by])
                               .drop(columns=col)
                               .rename(columns={'new_tmp': col})
                               )
        if not inplace:
            return dp

    def get_histogram(self, object_name: str, col, binsize, density: bool = False, groupby: str = 'Group'):
        df_in = self[object_name]
        df_out = _get_histogram(df_in, col=col, binsize=binsize, density=density, groupby=groupby)
        return df_out

    def add_from_parent(self, object_name: str, col: list = [], inplace=False):
        dp = self if inplace else self.copy()
        parent = dp._parents[object_name]
        dp.get_parent_indices(obj=object_name, inplace=True)
        for c in col:
            dp[object_name] = (dp[object_name]
                               .merge(dp[parent][['PositionIdx', 'Indices', c]],
                                      suffixes=(None, '_tmp'),
                                      left_on=['PositionIdx', 'ParentIndices'],
                                      right_on=['PositionIdx', 'Indices'])
                               .transform(lambda df: df.loc[:, ~df.columns.str.contains('_tmp')])
                               )
        if not inplace:
            return dp

    def add_columns(self, object_name: str, metrics, inplace=False, **kwargs):
        dp = self if inplace else self.copy()
        df = dp[object_name]
        for m in arg_to_list(metrics):
            if m == 'Heatmap':
                df = pyb.metrics.heatmap_metrics(df, **kwargs)
            elif m == 'is_col_larger':
                df = pyb.metrics.is_col_larger(df, **kwargs)
            elif m == 'bin_column':
                df = pyb.metrics.bin_column(df, **kwargs)
            elif m == 'Dapp':
                df = pyb.metrics.tracking_Dapp(df, **kwargs)
            else:
                ValueError(f'Metric "{m}" not found')
        dp[object_name] = df
        if not inplace:
            return dp

    def get_timeseries(self, object_name: str, metric, inplace=False, **kwargs):
        dp = self if inplace else self.copy()
        df_in = dp[object_name]
        if metric == 'SpineLength':
            df_out = pyb.metrics.Cell_length(df_in, **kwargs)
        elif metric == 'ObjectCount':
            df_out = pyb.metrics.Object_count(df_in, **kwargs)
        elif metric == 'ObjectClass':
            df_out = pyb.metrics.Object_classifier(df_in, **kwargs)
        elif metric == 'Intensity':
            df_out = pyb.metrics.Object_intensity(df_in, **kwargs)
        elif metric == 'Quantile':
            df_out = pyb.metrics.Column_quantile(df_in, **kwargs)
        elif metric == 'Aggregation':
            df_out = pyb.metrics.Column_aggregation(df_in, **kwargs)
        elif metric == 'Fluo_intensity':
            df_out = pyb.metrics.Fluo_intensity(df_in, **kwargs)
        else:
            ValueError(f'Metric "{metric}" not found')
        dp[f'{object_name}_timeseries'] = df_out
        if not inplace:
            return dp

    def plot_preset(self, preset: str, object_name: str = '',
                    drop_duplicates_by=[], return_axes: bool = False, **kwargs):
        dp = self.copy()
        hue = kwargs.get('hue', '')
        if isinstance(hue, list):
            dp.fuse_columns(obj=object_name, cols=hue, new='_'.join(hue), inplace=True)
            kwargs['hue'] = '_'.join(hue)
        if object_name:
            df_in = dp[object_name]
            if drop_duplicates_by:
                df_in = df_in.drop_duplicates(subset=drop_duplicates_by)
        _, ax = plt.subplots(dpi=130)
        if preset == 'histogram':
            ax = pyb.plots.plot_histogram(df_in, ax=ax, **kwargs)
        elif preset == 'histogram_fit':
            ax = pyb.plots.plot_histogram_fit(df_in, ax=ax, **kwargs)
        elif preset == 'bar':
            ax = pyb.plots.barplot(df_in, ax=ax, **kwargs)
        elif preset == 'line':
            ax = pyb.plots.lineplot(df_in, ax=ax, **kwargs)
        elif preset == 'line_fit':
            ax = pyb.plots.plot_line_fit(df_in, ax=ax, **kwargs)
        elif preset == 'scatter':
            ax = pyb.plots.scatterplot(df_in, ax=ax, **kwargs)
        elif preset == 'datapoints_and_mean':
            ax = pyb.plots.plot_datapoints_and_mean(df_in, dsList=dp.dsList, ax=ax, **kwargs)
        elif preset == 'heatmap':
            ax = pyb.plots.plot_heatmap(df_in, ax=ax, **kwargs)
        elif preset == 'timeseries':
            ax = pyb.plots.plot_timeseries(df_in, ax=ax, **kwargs)
        elif preset == 'boxplot':
            ax = pyb.plots.boxplot(df_in, ax=ax, **kwargs)
        elif preset == 'boxenplot':
            ax = pyb.plots.plot_boxenplot(df_in, ax=ax, **kwargs)
        elif preset == 'spot_tracks':
            lineage = kwargs.pop('lineage', '')
            dp.fuse_columns(obj=object_name, cols=['Idx', 'BacteriaLineage'], new='Track', inplace=True)
            if lineage:
                df_in = df_in.query('BacteriaLineage == @lineage')
            ax = pyb.plots.lineplot(df_in, hue='Track', sort=False, ax=ax, **kwargs)
        elif preset == 'rates_summary':
            ax = pyb.plots.plot_rates_summary(ax=ax, **kwargs)
        elif preset == 'grey_lines_and_highlight':
            ax = pyb.plots.plot_grey_lines_and_highlight(df_in, ax=ax, **kwargs)
        else:
            warn('Plot preset not found!')
        if return_axes:
            return ax
