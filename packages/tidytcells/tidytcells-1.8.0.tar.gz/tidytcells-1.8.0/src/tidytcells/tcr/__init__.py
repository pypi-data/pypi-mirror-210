"""
Functions to clean and standardise TCR gene data.
"""


from ._main import standardise, query, get_aa_sequence


def standardize(*args, **kwargs):
    """
    Alias for :py:func:`tidytcells.tcr.standardise`.
    """
    return standardise(*args, **kwargs)
