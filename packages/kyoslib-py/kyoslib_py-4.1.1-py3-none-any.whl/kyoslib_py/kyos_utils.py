import collections.abc
from datetime import datetime, timedelta

import numpy as np


def dict_merge(initial_dict, *args, overwrite_existing=False):
    """instead of updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into ``dct``.

    Args:
        initial_dict (dict): dict onto which the merge is executed
        *args (dict): Any number of dictonaries to be merged into initial_dict
        overwrite_existing (bool): Display the column name in bold font when showing it in the platform front-end

    Returns:
        rtn_dct (dict): merged dictonary

    Examples:
        >>> initial = {"accumulator": {"knock_out_price": 150, "trigger_price": 130, "accumulation_price": 110}}
        >>> new_key_dict = {"accumulator": {"sim": {"id": 10}}}
        >>> final = dict_merge(initial, new_key_dict)
        {"accumulator": {"knock_out_price": 150, "trigger_price": 130, "accumulation_price": 110, "sim": {"id": 10}}}
    """
    assert (
        initial_dict is not None and len(args) >= 1
    ), "dict_merge method requires at least two dicts to merge"
    merge_dicts = args[0:]
    rtn_dct = initial_dict.copy()
    for merge_dct in merge_dicts:
        for k, v in merge_dct.items():
            if not rtn_dct.get(k):
                rtn_dct[k] = v
            elif k in rtn_dct and type(v) != type(rtn_dct[k]) and not overwrite_existing:
                raise TypeError(
                    f"Overlapping keys exist with different types: original is {type(rtn_dct[k])}, new value is {type(v)}"
                )
            elif isinstance(rtn_dct[k], dict) and isinstance(
                merge_dct[k], collections.abc.Mapping
            ):
                rtn_dct[k] = dict_merge(
                    rtn_dct[k], merge_dct[k], overwrite_existing=overwrite_existing
                )
            elif isinstance(v, list):
                for list_value in v:
                    if list_value not in rtn_dct[k]:
                        rtn_dct[k].append(list_value)
            else:
                if overwrite_existing:
                    rtn_dct[k] = v
    return rtn_dct


def matlab_datenum_to_datetime(datenums) -> list:
    """
    Args:
        datenums (list or 1d np.array): Vector of matlab datenums.

    Returns:
        (list): List of dates in datetime format.
    """

    def datenum_to_datetime_scalar(datenum: float) -> datetime:
        """
        Convert Matlab datenum into Python datetime.
        Args:
             datenum (float): Date in datenum format
        Return:
            Datetime object corresponding to datenum.

        Note: Be careful when you use this function or pd.to_datetime(datenum- 719529, unit='D') with half hourly data.
            it maybe that result come out incorrect due to rounding issues
        """
        # see http://sociograph.blogspot.com/2011/04/how-to-avoid-gotcha-when-converting.html
        # https://stackoverflow.com/questions/13965740/converting-matlabs-datenum-format-to-python/13965852#13965852

        datenum = float(datenum)
        days = datenum % 1
        datetime_obj = (
            datetime.fromordinal(int(datenum)) + timedelta(days=days) - timedelta(days=366)
        )
        if datetime_obj.second:
            raise ValueError("function can't deal with level of precision in datenum.")
        return datetime_obj

    return [datenum_to_datetime_scalar(x) for x in datenums]


def mc_to_year_month(mc: np.array) -> np.array:
    month = (mc - 1) % 12 + 1
    year = (mc - month) / 12 + 2000
    return year.astype(int), month.astype(int)


def date_to_mc(date):
    return (date.year - 2000) * 12 + date.month


def stop_model(msg):
    """
    Used when a problem is encountered and the model should not proceed further because results
    will be meaningless and computational time wasted.
    The function creates a Status.txt file containing the error message. This file is then
    picked up by PHP to display the error message in the front end.

    Args:
        msg (str): Message that defines the error.
    """

    with open('Status.txt', 'w') as fid:
        fid.write(msg)
        fid.close()

    print(msg)
    return
