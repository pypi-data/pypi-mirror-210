"""
:meta private:
"""
from typing import List, Optional, Union

from pharmpy.deps import sympy
from pharmpy.model import Model
from pharmpy.modeling import remove_unused_parameters_and_rvs
from pharmpy.modeling.help_functions import _format_input_list, _get_etas


def remove_iiv(model: Model, to_remove: Optional[Union[List[str], str]] = None):
    """
    Removes all IIV etas given a list with eta names and/or parameter names.

    Parameters
    ----------
    model : Model
        Pharmpy model to create block effect on.
    to_remove : str, list
        Name/names of etas and/or name/names of individual parameters to remove.
        If None, all etas that are IIVs will be removed. None is default.

    Return
    ------
    Model
        Pharmpy model object

    Examples
    --------
    >>> from pharmpy.modeling import *
    >>> model = load_example_model("pheno")
    >>> model = remove_iiv(model)
    >>> model.statements.find_assignment("CL")
    CL = TVCL

    >>> model = load_example_model("pheno")
    >>> model = remove_iiv(model, "V")
    >>> model.statements.find_assignment("V")
    V = TVV

    See also
    --------
    remove_iov
    add_iiv
    add_iov
    add_pk_iiv

    """
    rvs, sset = model.random_variables, model.statements
    to_remove = _format_input_list(to_remove)
    etas = _get_etas(model, to_remove, include_symbols=True)

    for eta in etas:
        sset = sset.subs({sympy.Symbol(eta): 0})

    keep = [name for name in model.random_variables.names if name not in etas]
    model = model.replace(random_variables=rvs[keep], statements=sset)

    model = remove_unused_parameters_and_rvs(model)
    model = model.update_source()
    return model
