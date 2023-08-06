#! /usr/bin/env python
# -*- coding:Utf-8 -*-
# pylint: disable=fixme,invalid-name,line-too-long
"""Tools python."""
# ============================================================
#    Linux python path and Library import
# ============================================================

import calendar
import datetime
from collections import OrderedDict
from typing import Any, Iterable, Tuple

import arrow

# ============================================================
#     Functions and Procedures
# ============================================================


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    signal_first
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def signal_first(it: Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    """
    Get the first element in iterable loop :

    Args:
        it (Iterable[Any]): Iterable to loop

    Returns:
        Iterable[Tuple[bool, Any]]: Iterable to loop

    Yields:
        Iterator[Iterable[Tuple[bool, Any]]]: Iterable to loop

    >>> for is_first_element, var in signal_first(fib(10)):
    >>> if is_first_element:
    >>>     special_function(var)
    >>> else:
    >>>     not_so_special_function(var)

    """

    iterable = iter(it)
    yield True, next(iterable)
    for val in iterable:
        yield False, val


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    signal_last
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def signal_last(it: Iterable[Any]) -> Iterable[Tuple[bool, Any]]:
    """
    Get the last element in iterable loop :

    Args:
        it (Iterable[Any]): Iterable to loop

    Returns:
        Iterable[Tuple[bool, Any]]: Iterable to loop

    Yields:
        Iterator[Iterable[Tuple[bool, Any]]]: Iterable to loop

    >>> for is_last_element, var in signal_last(fib(10)):
    >>> if is_last_element:
    >>>     special_function(var)
    >>> else:
    >>>     not_so_special_function(var)

    """

    iterable = iter(it)
    ret_var = next(iterable)
    for val in iterable:
        yield False, ret_var
        ret_var = val
    yield True, ret_var


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    add_months
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def add_months(pdate, pmonths):
    """
    Add pmonths months to pdate

    Args:
        pdate (date): date to add months
        pmonths (int): Nb months to add

    Returns:
        date: new date
    """
    cal_month = pdate.month - 1 + pmonths
    cal_year = pdate.year + cal_month // 12
    cal_month = cal_month % 12 + 1
    cal_day = min(pdate.day, calendar.monthrange(cal_year, cal_month)[1])
    return pdate.replace(year=cal_year, month=cal_month, day=cal_day)


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    iso_date_info
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def iso_date_info(pdate):
    """
    return iso info from a date

    Args:
        pdate (date): date

    Returns:
        tuple: isoYear, isoWeek
    """
    isoYEAR, isoWEEK, isoDAY = pdate.isocalendar()
    del isoDAY
    isoYEAR = str(isoYEAR)
    isoWEEK = str(isoWEEK).rjust(2, "0")
    return (isoYEAR, isoWEEK)


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    convertHeaders_ToList
# ||||||||||||||||||||||||||||||||||||||||||||||||||
# pylint: disable-next=dangerous-default-value
def convertHeaders_ToList(
    pheaders,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pdictconv={},
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert row Headers to a list

    Args:
        pheaders (dict): headers to work with
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pdictconv (dict, optional): _description_. Defaults to {}.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.
    Returns:
        list: Headers
    """
    new_headers = []
    for header in pheaders:
        v = header[0]
        v = pdictconv.get(v, v)
        v = val_convert(
            v,
            pdecoding=pdecoding,
            pencoding=pencoding,
            pdoublequote=pdoublequote,
            ptobind=ptobind,
            pnone=pnone,
            pcase=pcase,
            pstrip=pstrip,
            pisdttutc=pisdttutc,
        )
        if v is not None:
            new_headers.append(v)
    return new_headers


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    convertRows_ToDicts
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def convertRows_ToDicts(
    prows,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert rows to a list of dict

    Args:
        prows (rows): rows to work with
        pdecoding (str, optional): decoding string. Defaults to None.
        pencoding (_type_, optional): encoding string. Defaults to None.
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.

    Returns:
        list: list of dict
    """

    new_rows = []
    for row in prows:
        new_rows.append(
            convertRow_ToDict(
                row,
                pdecoding=pdecoding,
                pencoding=pencoding,
                pdoublequote=pdoublequote,
                ptobind=ptobind,
                pnone=pnone,
                pcase=pcase,
                pstrip=pstrip,
                pisdttutc=pisdttutc,
            )
        )
    return new_rows


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    convertRows_ToLists
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def convertRows_ToLists(
    prows,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert rows to a list of list

    Args:
        prows (rows): rows to work with
        pdecoding (str, optional): decoding string. Defaults to None.
        pencoding (_type_, optional): encoding string. Defaults to None.
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.

    Returns:
        list: list of list
    """

    new_rows = []
    for row in prows:
        new_rows.append(
            convertRow_ToList(
                row,
                pdecoding=pdecoding,
                pencoding=pencoding,
                pdoublequote=pdoublequote,
                ptobind=ptobind,
                pnone=pnone,
                pcase=pcase,
                pstrip=pstrip,
                pisdttutc=pisdttutc,
            )
        )
    return new_rows


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    convertRow_ToDict
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def convertRow_ToDict(
    prow,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert a row to a dict

    Args:
        prow (row): row to work with
        pdecoding (str, optional): decoding string. Defaults to None.
        pencoding (_type_, optional): encoding string. Defaults to None.
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.

    Returns:
        dict: dict
    """
    new_dict = OrderedDict()
    for k, v in zip(prow.cursor_description, prow):
        v = val_convert(
            v,
            pdecoding=pdecoding,
            pencoding=pencoding,
            pdoublequote=pdoublequote,
            ptobind=ptobind,
            pnone=pnone,
            pcase=pcase,
            pstrip=pstrip,
            pisdttutc=pisdttutc,
        )
        new_dict[k[0]] = v
    return new_dict


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    convertRow_ToList
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def convertRow_ToList(
    prow,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert a row to a list

    Args:
        prow (row): row to work with
        pdecoding (str, optional): decoding string. Defaults to None.
        pencoding (_type_, optional): encoding string. Defaults to None.
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.

    Returns:
        list: list
    """
    new_list = []
    for v in prow:
        v = val_convert(
            v,
            pdecoding=pdecoding,
            pencoding=pencoding,
            pdoublequote=pdoublequote,
            ptobind=ptobind,
            pnone=pnone,
            pcase=pcase,
            pstrip=pstrip,
            pisdttutc=pisdttutc,
        )
        new_list.append(v)
    return new_list


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    convertDict_ToDict
# ||||||||||||||||||||||||||||||||||||||||||||||||||
# pylint: disable-next=dangerous-default-value
def convertDict_ToDict(
    pdict,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pdictconv={},
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert a dict to an ordered dict

    Args:
        pdict (dict): dict to work with
        pdecoding (str, optional): decoding string. Defaults to None.
        pencoding (_type_, optional): encoding string. Defaults to None.
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.

    Returns:
        ordereddict: dict
    """
    new_dict = OrderedDict()
    for k, v in pdict.items():
        v = val_convert(
            v,
            pdecoding=pdecoding,
            pdoublequote=pdoublequote,
            pencoding=pencoding,
            ptobind=ptobind,
            pnone=pnone,
            pcase=pcase,
            pstrip=pstrip,
            pisdttutc=pisdttutc,
        )
        new_dict[pdictconv.get(k, k)] = v
    return new_dict


# ||||||||||||||||||||||||||||||||||||||||||||||||||
#    val_convert
# ||||||||||||||||||||||||||||||||||||||||||||||||||
def val_convert(
    pval,
    pdecoding=None,
    pencoding=None,
    pdoublequote=False,
    ptobind=False,
    pnone=None,
    pcase=None,
    pstrip=False,
    pisdttutc=False,
):
    """
    Convert Val

    Args:
        pval (obj): val to work with
        pdecoding (str, optional): decoding string. Defaults to None.
        pencoding (_type_, optional): encoding string. Defaults to None.
        pdoublequote (bool, optional): transform every ' to ''. Defaults to False.
        ptobind (bool, optional): return everytrhing into string. Defaults to False.
        pnone (obj, optional): Value to return if None. Defaults to None.
        pcase (str, optional): UP or LOW to return uppercase or lowercase string. Defaults to None.
        pstrip (bool, optional): strip string. Defaults to False.
        pisdttutc (bool, optional): return utc datetime. Defaults to False.

    Returns:
        obj: val converted
    """
    v = pval
    if pnone is not None:
        if v is None:
            v = pnone
    if pstrip:
        if isinstance(v, str):
            v = v.strip()
    if pdoublequote:
        if isinstance(v, str):
            v = v.replace("'", "''")
    if ptobind:
        if v is None:
            v = "NULL"
        elif isinstance(v, str):
            v = f"'{v}'"
    if pisdttutc:
        if isinstance(v, datetime.date):
            v = arrow.get(v).datetime
    if pdecoding is not None:
        try:
            v = v.decode(pdecoding)
        # pylint: disable-next=broad-exception-caught
        except Exception:
            pass
    if pencoding is not None:
        try:
            v = v.encode(pencoding)
        # pylint: disable-next=broad-exception-caught
        except Exception:
            pass
    if pcase is not None:
        if isinstance(v, str):
            if "UP" in pcase.upper():
                v = v.upper()
            if "LOW" in pcase.upper():
                v = v.lower()
    return v
