"""
:meta private:
"""

import re
from typing import List, Optional, Union

from pharmpy.deps import sympy
from pharmpy.model import Assignment, Model, Parameter, Parameters
from pharmpy.modeling.help_functions import _format_input_list, _get_etas

from .expressions import create_symbol


def transform_etas_boxcox(model: Model, list_of_etas: Optional[Union[List[str], str]] = None):
    """Applies a boxcox transformation to selected etas

    Initial estimate for lambda is 0.1 with bounds (-3, 3).

    Parameters
    ----------
    model : Model
        Pharmpy model to apply boxcox transformation to.
    list_of_etas : str, list
        Name/names of etas to transform. If None, all etas will be transformed (default).

    Return
    ------
    Model
        Pharmpy model object

    Examples
    --------
    >>> from pharmpy.modeling import *
    >>> model = load_example_model("pheno")
    >>> model = transform_etas_boxcox(model, ["ETA_1"])
    >>> model.statements.before_odes.full_expression("CL")
    PTVCL*WGT*exp((exp(ETA_1)**lambda1 - 1)/lambda1)

    See also
    --------
    transform_etas_tdist
    transform_etas_john_draper

    """
    list_of_etas = _format_input_list(list_of_etas)
    etas = _get_etas(model, list_of_etas)
    eta_transformation = EtaTransformation.boxcox(len(etas))
    model = _transform_etas(model, eta_transformation, etas)
    return model.update_source()


def transform_etas_tdist(model: Model, list_of_etas: Optional[Union[List[str], str]] = None):
    """Applies a t-distribution transformation to selected etas

    Initial estimate for degrees of freedom is 80 with bounds (3, 100).

    Parameters
    ----------
    model : Model
        Pharmpy model to apply t distribution transformation to.
    list_of_etas : str, list
        Name/names of etas to transform. If None, all etas will be transformed (default).

    Return
    ------
    Model
        Pharmpy model object

    Examples
    --------
    >>> from pharmpy.modeling import *
    >>> model = load_example_model("pheno")
    >>> model = transform_etas_tdist(model, ["ETA_1"])
    >>> model.statements.before_odes.full_expression("CL")    # doctest: +ELLIPSIS
    PTVCL*WGT*exp(ETA_1*(1 + (ETA_1**2 + 1)/(4*df1) + (5*ETA_1**4 + 16*ETA_1**2 + 3)/(96*...

    See also
    --------
    transform_etas_boxcox
    transform_etas_john_draper

    """
    list_of_etas = _format_input_list(list_of_etas)
    etas = _get_etas(model, list_of_etas)
    eta_transformation = EtaTransformation.tdist(len(etas))
    model = _transform_etas(model, eta_transformation, etas)
    return model.update_source()


def transform_etas_john_draper(model: Model, list_of_etas: Optional[Union[List[str], str]] = None):
    """Applies a John Draper transformation [1]_ to spelected etas

    Initial estimate for lambda is 0.1 with bounds (-3, 3).

    .. [1] John, J., Draper, N. (1980). An Alternative Family of Transformations.
       Journal of the Royal Statistical Society. Series C (Applied Statistics),
       29(2), 190-197. doi:10.2307/2986305

    Parameters
    ----------
    model : Model
        Pharmpy model to apply John Draper transformation to.
    list_of_etas : str, list
        Name/names of etas to transform. If None, all etas will be transformed (default).

    Return
    ------
    Model
        Pharmpy model object

    Examples
    --------
    >>> from pharmpy.modeling import *
    >>> model = load_example_model("pheno")
    >>> model = transform_etas_john_draper(model, ["ETA_1"])
    >>> model.statements.before_odes.full_expression("CL")
    PTVCL*WGT*exp(((Abs(ETA_1) + 1)**lambda1 - 1)*sign(ETA_1)/lambda1)

    See also
    --------
    transform_etas_boxcox
    transform_etas_tdist

    """
    list_of_etas = _format_input_list(list_of_etas)
    etas = _get_etas(model, list_of_etas)
    eta_transformation = EtaTransformation.john_draper(len(etas))
    model = _transform_etas(model, eta_transformation, etas)
    return model.update_source()


def _transform_etas(model, transformation, etas):
    etas_assignment, etas_subs = _create_new_etas(etas, transformation.name)
    parameters, thetas = _create_new_thetas(model, transformation.theta_type, len(etas))
    transformation.apply(etas_assignment, thetas)
    statements_new = transformation.assignments
    sset = model.statements.subs(etas_subs)
    model = model.replace(parameters=parameters, statements=statements_new + sset)
    return model


def _create_new_etas(etas_original, transformation):
    etas_subs = {}
    etas_assignment = {}
    if transformation == 'boxcox':
        eta_new = 'etab'
    elif transformation == 'tdist':
        eta_new = 'etat'
    elif transformation == 'johndraper':
        eta_new = 'etad'
    else:
        eta_new = 'etan'
    for i, eta in enumerate(etas_original, 1):
        etas_subs[sympy.Symbol(eta)] = sympy.Symbol(f'{eta_new.upper()}{i}')
        etas_assignment[sympy.Symbol(f'{eta_new}{i}')] = sympy.Symbol(f'{eta_new.upper()}{i}')
        etas_assignment[sympy.Symbol(f'eta{i}')] = sympy.Symbol(eta)

    return etas_assignment, etas_subs


def _create_new_thetas(model, transformation, no_of_thetas):
    pset = list(model.parameters)
    thetas = {}
    theta_name = str(create_symbol(model, stem=transformation, force_numbering=True))

    param_settings = (0.01, -3, 3) if transformation == 'lambda' else (80, 3, 100)

    if no_of_thetas == 1:
        pset.append(Parameter(theta_name, *param_settings))
        thetas['theta1'] = theta_name
    else:
        theta_no = int(re.findall(r'\d', theta_name)[0])

        for i in range(1, no_of_thetas + 1):
            pset.append(Parameter(theta_name, 0.01, -3, 3))
            thetas[f'theta{i}'] = theta_name
            theta_name = f'{transformation}{theta_no + i}'

    return Parameters.create(pset), thetas


class EtaTransformation:
    def __init__(self, name, assignments, theta_type):
        self.name = name
        self.assignments = assignments
        self.theta_type = theta_type

    def apply(self, etas, thetas):
        for i, assignment in enumerate(self.assignments):
            self.assignments[i] = assignment.subs(etas).subs(thetas)

    @classmethod
    def boxcox(cls, no_of_etas):
        assignments = []
        for i in range(1, no_of_etas + 1):
            symbol = sympy.Symbol(f'etab{i}')
            expression = (sympy.exp(sympy.Symbol(f'eta{i}')) ** sympy.Symbol(f'theta{i}') - 1) / (
                sympy.Symbol(f'theta{i}')
            )

            assignment = Assignment(symbol, expression)
            assignments.append(assignment)

        return cls('boxcox', assignments, 'lambda')

    @classmethod
    def tdist(cls, no_of_etas):
        assignments = []
        for i in range(1, no_of_etas + 1):
            symbol = sympy.Symbol(f'etat{i}')

            eta = sympy.Symbol(f'eta{i}')
            theta = sympy.Symbol(f'theta{i}')

            num_1 = eta**2 + 1
            denom_1 = 4 * theta

            num_2 = (5 * eta**4) + (16 * eta**2 + 3)
            denom_2 = 96 * theta**2

            num_3 = (3 * eta**6) + (19 * eta**4) + (17 * eta**2) - 15
            denom_3 = 384 * theta**3

            expression = eta * (1 + (num_1 / denom_1) + (num_2 / denom_2) + (num_3 / denom_3))

            assignment = Assignment(symbol, expression)
            assignments.append(assignment)

        return cls('tdist', assignments, 'df')

    @classmethod
    def john_draper(cls, no_of_etas):
        assignments = []
        for i in range(1, no_of_etas + 1):
            symbol = sympy.Symbol(f'etad{i}')

            eta = sympy.Symbol(f'eta{i}')
            theta = sympy.Symbol(f'theta{i}')

            expression = sympy.sign(eta) * (((abs(eta) + 1) ** theta - 1) / theta)

            assignment = Assignment(symbol, expression)
            assignments.append(assignment)

        return cls('johndraper', assignments, 'lambda')

    def __str__(self):
        return str(self.assignments)
