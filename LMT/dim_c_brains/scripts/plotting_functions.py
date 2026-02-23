"""
@author: xmousset
"""

import re
from typing import Any, List

import numpy as np
import pandas as pd
from pandas import DataFrame
from plotly.colors import qualitative
from plotly import graph_objects as go


def str_h_min(total_minutes: int | float):
    """
    Converts a time duration in minutes to a string formatted as "HH:MM".

    Args:
        total_minutes (int | float): The total number of minutes to convert.
    Returns:
        str: The time formatted as a zero-padded string in "HH:MM" format.
    Example:
        >>> str_h_min(135)
        "02:15"
    """

    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    return f"{hours:02d}:{minutes:02d}"


def floor_power10(x: float | int) -> float:
    """Rounds the input number down to the largest multiple of a power of ten
    less than or equal to x.
    if x <= 0, return 1.

    Examples:
        >>> print(floor_power10(3756))
        3000
        >>> print(floor_power10(89))
        80
    """
    if isinstance(x, int):
        x = float(x)

    if x == 0:
        floored_value = float(0)
    elif x >= 1:
        ten_power = 10 ** (len(str(int(x))) - 1)
        floored_value: float = (x // ten_power) * ten_power
    elif x > 0:
        _, decimals = str(x).split(".")
        i = 0
        while i + 1 < len(decimals) and decimals[i] == "0":
            i += 1
        ten_power = 10 ** (-(i + 1))
        floored_value: float = (x // ten_power) * ten_power
    else:
        floored_value = -floor_power10(-x)

    return floored_value


def draw_nights(
    fig: go.Figure,
    night_begin: int,
    night_duration: int,
    start_time: pd.Timestamp | None = None,
    end_time: pd.Timestamp | None = None,
):
    """
    Adds shaded rectangles to a Plotly figure to indicate night periods.

    Args:
        fig (go.Figure): The Plotly figure to modify.
        start_time (pd.Timestamp): The start time of the plot.
        end_time (pd.Timestamp): The end time of the plot.
        night_begin (int): The hour at which night begins (0-23).
        night_duration (int): Duration of the night in hours.

    Returns:
        go.Figure: The figure with night periods shaded.
    """
    # Collect all x values from all traces in fig.data
    x_values = []
    for trace in getattr(fig, "data"):
        if hasattr(trace, "x") and trace.x is not None:
            x_values.extend(trace.x)

    if not x_values:
        print("[WARN] draw_nights: No x values found in figure")
        return fig

    # Convert to pandas Timestamps if needed
    if not isinstance(x_values[0], pd.Timestamp):
        x_values = pd.to_datetime(x_values)
    if start_time is None:
        start_time = min(x_values)
    if end_time is None:
        end_time = max(x_values)

    h = start_time.floor("1h")
    start_h = h.replace(hour=night_begin)
    if start_time.hour < night_begin:
        start_h = start_h - pd.Timedelta(days=1)
    delta_h = pd.Timedelta(hours=night_duration)
    first_night = True
    while h < end_time:

        if h.hour == night_begin:
            x_start = h
            x_end = h + delta_h
            if x_end > end_time:
                x_end = end_time
            fig.add_vrect(
                x0=x_start,
                x1=x_end,
                line_width=0,
                fillcolor="black",
                layer="below",
                opacity=0.1,
            )
            h += delta_h

        elif first_night and h > start_h and h < start_h + delta_h:
            first_night = False
            x_start = start_time.floor("15min")
            x_end = start_h + delta_h
            if x_end > end_time:
                x_end = end_time
            fig.add_vrect(
                x0=x_start,
                x1=x_end,
                line_width=0,
                fillcolor="black",
                layer="below",
                opacity=0.1,
            )

        else:
            h += pd.Timedelta(hours=1)

    return fig


def hex_to_rgba(hex_color: str, alpha: float = 0.2):
    hex_color = hex_color.lstrip("#")
    r, g, b = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def get_transparent_color_sequence(
    color_sequence: List[str], alpha: float = 0.2
):
    rgba_colors = [hex_to_rgba(c, alpha) for c in color_sequence]
    return rgba_colors


def line_with_shade(
    df: DataFrame,
    x_col: str,
    y_col: str,
    y_std_col: str | None = None,
    y_min_col: str | None = None,
    y_max_col: str | None = None,
    color: str | None = None,
    color_discrete_sequence: list[str] | None = None,
    **kwargs: Any,
):
    """
    Plot a line curve with shaded error or range using Plotly.

    Parameters
    ----------
    df : DataFrame
        Input data containing columns for x, y, color, and error/range.
    x_col : str
        Name of the column to use for the x-axis.
    y_col : str
        Name of the column to use for the y-axis.
    color : str
        Name of the column to group and color the lines.
    y_std_col : str or None, optional
        Name of the column with standard deviation values for shading.
        Required if y_min_col and y_max_col are not provided.
    y_min_col : str or None, optional
        Name of the column with minimum values for shading.
        Required if y_std_col is not provided.
    y_max_col : str or None, optional
        Name of the column with maximum values for shading.
        Required if y_std_col is not provided.
    color_discrete_sequence : list of str or None, optional
        List of colors to use for the lines. If None, a default color sequence is used.
    Returns
    -------
    fig : plotly.graph_objs.Figure
        Plotly figure object with the shaded curve plot.
    Raises
    ------
    ValueError
        If neither y_std_col nor both y_min_col and y_max_col are provided.
    """

    if y_std_col is None and (y_min_col is None or y_max_col is None):
        raise ValueError(
            "Either y_std_col or both y_min_col and y_max_col must be provided"
        )

    if y_std_col is not None:
        use_std = True
    else:
        use_std = False

    if color_discrete_sequence is None:
        color_sequence = qualitative.Plotly
    else:
        color_sequence = color_discrete_sequence
    transparent_sequence = get_transparent_color_sequence(color_sequence)

    df_copy = df.copy()
    # Fill NaN values with 0 for relevant columns (avoid RFID column)
    for col in [x_col, y_col, y_std_col, y_min_col, y_max_col]:
        if isinstance(col, str) and col in df_copy.columns:
            df_copy[col] = df_copy[col].fillna(0)

    fig = go.Figure()

    # Determine unique groups and number of colors to plot
    n_clr = 1
    unique_colors = None
    if color is not None:
        if "category_orders" in kwargs:
            cat_orders = kwargs["category_orders"]
            if color in cat_orders:
                unique_colors = cat_orders[color]

        if unique_colors is None:
            unique_colors = df_copy[color].unique()

        n_clr = len(unique_colors)

    for i in range(n_clr):
        if unique_colors is None:
            sub_df = df_copy
            legend_name = y_col
        else:
            sub_df = df_copy[df_copy[color] == unique_colors[i]]
            legend_name = str(unique_colors[i])

        if use_std:
            std_up = sub_df[y_col] + sub_df[y_std_col]
            std_down = sub_df[y_col] - sub_df[y_std_col]
        else:
            std_up = sub_df[y_max_col]
            std_down = sub_df[y_min_col]

        # standard deviation area
        fig.add_trace(
            go.Scatter(
                x=list(sub_df[x_col]) + list(sub_df[x_col])[::-1],
                y=list(std_up) + list(std_down)[::-1],
                fill="toself",
                fillcolor=transparent_sequence[i % len(transparent_sequence)],
                line=dict(color="rgba(255,255,255,0)"),  # no border
                hoverinfo="skip",  # do not display info when mouse on it
                showlegend=True,
                name=legend_name + " ± STD",
            )
        )

        # line trace
        fig.add_trace(
            go.Scatter(
                x=sub_df[x_col],
                y=sub_df[y_col],
                mode="lines",
                name=legend_name,
                line=dict(color=color_sequence[i % len(color_sequence)]),
            )
        )

    fig.update_layout(xaxis_title=x_col, yaxis_title=y_col)

    return fig
