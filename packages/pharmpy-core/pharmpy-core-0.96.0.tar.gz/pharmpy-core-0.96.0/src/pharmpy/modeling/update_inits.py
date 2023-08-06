"""
:meta private:
"""

from pharmpy.deps import pandas as pd
from pharmpy.model import Model


def update_inits(
    model: Model, parameter_estimates: pd.Series, move_est_close_to_bounds: bool = False
):
    """Update initial parameter estimate for a model

    Updates initial estimates of population parameters for a model.
    If the new initial estimates are out of bounds or NaN this function will raise.

    Parameters
    ----------
    model : Model
        Pharmpy model to update initial estimates
    parameter_estimates : pd.Series
        Parameter estimates to update
    move_est_close_to_bounds : bool
        Move estimates that are close to bounds. If correlation >0.99 the correlation will
        be set to 0.9, if variance is <0.001 the variance will be set to 0.01.

    Returns
    -------
    Model
        Pharmpy model object

    Example
    -------
    >>> from pharmpy.modeling import load_example_model, update_inits
    >>> from pharmpy.tools import load_example_modelfit_results
    >>> model = load_example_model("pheno")
    >>> results = load_example_modelfit_results("pheno")
    >>> model.parameters.inits  # doctest:+ELLIPSIS
    {'PTVCL': 0.00469307, 'PTVV': 1.00916, 'THETA_3': 0.1, 'IVCL': 0.0309626, 'IVV': 0.031128, 'SIGMA_1_1': 0.013241}
    >>> model = update_inits(model, results.parameter_estimates)
    >>> model.parameters.inits  # doctest:+ELLIPSIS
    {'PTVCL': 0.00469555, 'PTVV': 0.984258, 'THETA_3': 0.15892, 'IVCL': 0.0293508, 'IVV': 0.027906, ...}

    """
    if move_est_close_to_bounds:
        parameter_estimates = _move_est_close_to_bounds(model, parameter_estimates)

    model = model.replace(parameters=model.parameters.set_initial_estimates(parameter_estimates))

    return model.update_source()


def _move_est_close_to_bounds(model: Model, pe):
    rvs, pset = model.random_variables, model.parameters
    est = pe.to_dict()
    sdcorr = rvs.parameters_sdcorr(est)
    newdict = est.copy()
    for dist in rvs:
        rvs = dist.names
        if len(rvs) > 1:
            sigma_sym = dist.variance
            for i in range(sigma_sym.rows):
                for j in range(sigma_sym.cols):
                    param_name = sigma_sym[i, j].name
                    if i != j:
                        if sdcorr[param_name] > 0.99:
                            name_i, name_j = sigma_sym[i, i].name, sigma_sym[j, j].name
                            # From correlation to covariance
                            corr_new = 0.9
                            sd_i, sd_j = sdcorr[name_i], sdcorr[name_j]
                            newdict[param_name] = corr_new * sd_i * sd_j
                    else:
                        if not _is_zero_fix(pset[param_name]) and est[param_name] < 0.001:
                            newdict[param_name] = 0.01
        else:
            param_name = dist.variance.name
            if not _is_zero_fix(pset[param_name]) and est[param_name] < 0.001:
                newdict[param_name] = 0.01
    return newdict


def _is_zero_fix(param):
    return param.init == 0 and param.fix


def update_initial_individual_estimates(
    model: Model, individual_estimates: pd.Series, force: bool = True
):
    """Update initial individual estimates for a model

    Updates initial individual estimates for a model.

    Parameters
    ----------
    model : Model
        Pharmpy model to update initial estimates
    individual_estimates : pd.DataFrame
        Individual estimates to use
    force : bool
        Set to False to only update if the model had initial individual estimates before

    Returns
    -------
    Model
        Pharmpy model object

    Example
    -------
    >>> from pharmpy.modeling import load_example_model, update_initial_individual_estimates
    >>> from pharmpy.tools import load_example_modelfit_results
    >>> model = load_example_model("pheno")
    >>> results = load_example_modelfit_results("pheno")
    >>> ie = results.individual_estimates
    >>> model = update_initial_individual_estimates(model, ie)
    """
    if not force and model.initial_individual_estimates is None:
        return model

    model = model.replace(initial_individual_estimates=individual_estimates)
    return model.update_source()
