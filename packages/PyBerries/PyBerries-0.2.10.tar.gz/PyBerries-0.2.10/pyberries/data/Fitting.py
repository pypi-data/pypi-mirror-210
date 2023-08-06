import inspect
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from .util import arg_to_list


class Fit():

    def __init__(self, df_in, x: str, y: str, model=None, model_type: str = None,
                 groupby: str = 'Group', p0=None):

        assert model or model_type, 'Must provide either a model_type or a model function'
        if model:
            self.model = model
        else:
            self.model_type = model_type
            self.model = get_model(model_type)
        if p0:
            model_args = len(inspect.getfullargspec(self.model).args) - 1
            assert len(p0) == model_args, \
                f'Number of initial parameters ({len(p0)}) does not match number of model arguments ({model_args})'
        self.groupby = groupby
        fit_results = dict()
        df_out = pd.DataFrame()
        for name, data in df_in.groupby(groupby, sort=False):
            groupName = '-'.join(map(str, name)) if isinstance(name, tuple) else str(name)
            try:
                popt, _ = curve_fit(self.model, data[x], data[y], p0=p0)
                fit_results[groupName] = popt
            except Exception:
                print(f'Fit for dataset {name} failed')
            data = data.assign(Fit=self.model(data[x], *popt))
            df_out = pd.concat([df_out, data], axis=0, ignore_index=True)
        self.data = df_out
        self.fit_params = fit_results
        self.groupby = groupby

    def get_rates(self, dt=1):
        dt = arg_to_list(dt)
        if self.model_type == 'monoexp_decay':
            rates = pd.DataFrame(columns=['Group', 'Rate'])
            for j, grp in enumerate(self.fit_params.keys()):
                popt = self.fit_params[grp]
                dt_grp = dt[j] if len(dt) > 1 else dt[0]
                rates.loc[j] = {'Group': grp, 'Rate': popt[1]/dt_grp}
            rates = rates.astype({'Group': 'category', 'Rate': 'float64'})
        elif self.model_type == 'biexp_decay':
            rates = pd.DataFrame(columns=['Group', 'Rate_type', 'Rate', 'Population'])
            i = 0
            for j, grp in enumerate(self.fit_params.keys()):
                popt = self.fit_params[grp]
                dt_grp = dt[j] if len(dt) > 1 else dt[0]
                rates.loc[i] = {'Group': grp, 'Rate_type': 'Fast',
                                'Rate': popt[1]/dt_grp, 'Population': popt[0]/(popt[0]+popt[2])}
                i += 1
                rates.loc[i] = {'Group': grp, 'Rate_type': 'Slow',
                                'Rate': popt[3]/dt_grp, 'Population': popt[2]/(popt[0]+popt[2])}
                i += 1
            rates = rates.astype({'Group': 'category', 'Rate_type': 'category',
                                  'Rate': 'float64', 'Population': 'float64'})
        elif self.model_type == 'monoexp_decay_offset':
            rates = pd.DataFrame(columns=['Group', 'Amplitude', 'Rate', 'Offset'])
            for j, grp in enumerate(self.fit_params.keys()):
                popt = self.fit_params[grp]
                dt_grp = dt[j] if len(dt) > 1 else dt[0]
                rates.loc[j] = {'Group': grp, 'Amplitude': popt[0], 'Rate': popt[1]/dt_grp, 'Offset': popt[2]}
            rates = rates.astype({'Group': 'category', 'Amplitude': 'float64',
                                  'Rate': 'float64', 'Offset': 'float64'})
        if isinstance(self.groupby, list):
            rates[self.groupby] = rates['Group'].str.split('-', expand=True)
        return rates

    def get_fit_parameters(self, param_names: list):
        n_params = len(list(self.fit_params.values())[0])
        assert len(param_names) >= n_params, \
            f'List of parameter names too short for the number of fitting parameters ({n_params})'
        if not param_names:
            param_names = [f'Param_{i}' for i in range(n_params)]
        rates = pd.DataFrame(columns=['Group', 'Fitted_param', 'Param_name'])
        i = 0
        for _, grp in enumerate(self.fit_params.keys()):
            popt = self.fit_params[grp]
            for k, param in enumerate(popt):
                rates.loc[i] = {'Group': grp, 'Fitted_param': param, 'Param_name': param_names[k]}
                i += 1
        rates = rates.astype({'Group': 'category', 'Fitted_param': 'float64', 'Param_name': 'category'})
        if isinstance(self.groupby, list):
            rates[self.groupby] = rates['Group'].str.split('-', expand=True)
        return rates


def get_model(model_type=''):
    if model_type == 'monoexp_decay':
        def model(x, a, b):
            return a*np.exp(-b*x, dtype='float64')
    elif model_type == 'biexp_decay':
        def model(x, a, b, c, d):
            return a*np.exp(-b*x, dtype='float64') + c*np.exp(-d*x, dtype='float64')
    elif model_type == 'monoexp_decay_offset':
        def model(x, a, b, c):
            return a*np.exp(-b*x) + c
    return model
