"""
Time handling
"""
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Protocol

import cftime  # type: ignore[import]
import numpy as np

if TYPE_CHECKING:
    from typing import Any, Tuple, Union

    import xarray as xr


def convert_year_month_to_time(
    inp: xr.Dataset,
    day: int = 1,
    **kwargs: Any,
) -> xr.Dataset:
    """
    Convert year and month co-ordinates into a time axis

    This is a facade to :func:`convert_to_time`

    Parameters
    ----------
    inp
        Data to convert

    day
        Day of the month to assume in output

    **kwargs
        Passed to intialiser of :class:`cftime.datetime`

    Returns
    -------
        Data with time axis
    """
    return convert_to_time(
        inp,
        time_coords=("year", "month"),
        cftime_converter=partial(cftime.datetime, day=day, **kwargs),
    )


class CftimeConverter(Protocol):  # pylint: disable=too-few-public-methods
    """
    Callable that supports converting stacked time co-ordinates to :obj:`cftime.datetime`
    """

    def __call__(  # type: ignore[no-any-unimported]
        self,
        *args: Union[np.float_, np.int_],
    ) -> cftime.datetime:
        """
        Convert input values to an :obj:`cftime.datetime`
        """


def convert_to_time(
    inp: xr.Dataset,
    time_coords: Tuple[str, ...],
    cftime_converter: CftimeConverter,
) -> xr.Dataset:
    """
    Convert some co-ordinates representing time into a time axis

    Parameters
    ----------
    inp
        Data to convert

    time_coords
        Co-ordinates from which to create the time axis

    cftime_converter
        Callable that converts the stacked time co-ordinates to
        :obj:`cftime.datetime`

    Returns
    -------
        Data with time axis
    """
    inp = inp.stack(time=time_coords)
    times = inp["time"].values

    inp = inp.drop_vars(("time",) + time_coords).assign_coords(
        {"time": [cftime_converter(*t) for t in times]}
    )

    return inp


def convert_time_to_year_month(
    inp: xr.Dataset,
    time_axis: str = "time",
) -> xr.Dataset:
    """
    Convert the time dimension to year and month co-ordinates

    Parameters
    ----------
    inp
        Data to convert

    Returns
    -------
        Data with year and month co-ordinates
    """
    out = inp.assign_coords(
        {
            "month": inp[time_axis].dt.month,
            "year": inp[time_axis].dt.year,
        }
    ).set_index({time_axis: ("year", "month")})

    # Could be updated when https://github.com/pydata/xarray/issues/7104 is
    # closed
    unique_vals, counts = np.unique(out[time_axis].values, return_counts=True)

    if (counts > 1).any():
        non_unique = list((v, c) for v, c in zip(unique_vals, counts) if c > 1)
        raise ValueError(
            "Your year-month axis is not unique. "
            f"Year-month values with a count > 1: {non_unique}"
        )

    return out.unstack(time_axis)
