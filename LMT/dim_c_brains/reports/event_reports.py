"""
@author: xmousset
"""

import plotly.express as px

from dim_c_brains.scripts.reports_manager import HTMLReportManager
from dim_c_brains.scripts.dataframe_constructor import DataFrameConstructor
from dim_c_brains.scripts.plotting_functions import (
    str_h_min,
    floor_power10,
    draw_nights,
    line_with_shade,
)
from dim_c_brains.reports.overview_reports import get_event_card


def generic_reports(
    report_manager: HTMLReportManager,
    df_constructor: DataFrameConstructor,
    event_name: str,
    **kwargs,
):
    """For any event, it creates a generic dataframe using the given
    `DataFrameConstructor` and construct all the generic reports into the given
    `HTMLReportManager` and returning the generated dataframe.

    Other Parameters
    ----------------
    time : str, optional
        The time column to use (default: "START_TIME").
    night_begin : int, optional
        The hour when the night begins (default: 20).
    night_duration : int, optional
        The duration of the night in hours (default: 12).
    first_value_in_graph : bool, optional
        Whether to include the first value in plots. It impacts the
        rendering of columns graphs. By default, the first value is included.
        (default: True).
    """

    report_manager.reports_creation_focus(event_name)
    df = df_constructor.process_event(event_name)

    if df is None:
        report_manager.add_title(
            name=f"Analysis of {event_name} event",
            content="""
            No data available for the selected time interval. Please adjust
            the processing limits or check the database connection.""",
        )
        return None

    #######################################
    #   Constants & Parameters   #
    #######################################

    TIME = kwargs.get("time", "START_TIME")

    NB_ANIMALS = df["RFID"].nunique()

    exp_start_time, exp_end_time = df_constructor.get_processing_limits("TIME")
    NB_DAYS = (exp_end_time - exp_start_time).total_seconds() / 3600 / 24

    if kwargs.get("first_value_in_graph", True):
        MASK = df.index == df.index
    else:
        MASK = df["START_FRAME"] != df["START_FRAME"].iloc[0]

    nights_parameters = {
        "start_time": df["START_TIME"].min(),
        "end_time": df["END_TIME"].max(),
        "night_begin": kwargs.get("night_begin", 20),
        "night_duration": kwargs.get("night_duration", 12),
    }

    plot_parameters = {
        "color": "RFID",
        "category_orders": {"RFID": list(df["RFID"].cat.categories)},
    }

    #######################################
    #   Titles   #
    #######################################

    report_manager.add_title(
        name=f"Analysis of <i>{event_name}</i> events",
        content=f"""
        This section presents the analysis of <i>{event_name}</i> events
        recorded in the dataset.<br>
        You can download the underlying data used for the plots in Excel format
        by clicking on the '<i>Download data</i>' link in the top-right hand
        corner.""",
    )

    report_manager.add_card(
        name="Time interval unit",
        content=f"""
        Calculated time bin is {df_constructor.binner.bin_size} frames.<br>
        It corresponds to {df_constructor.binner.bin_size
        / df_constructor.binner.fps / 60} minutes.
        """,
    )
    report_manager.add_card(
        name="Duration unit",
        content="All durations are in minutes (min).",
    )

    #######################################
    #   Event overview card   #
    #######################################

    card = get_event_card(df, [event_name], NB_ANIMALS, NB_DAYS)

    report_manager.add_card(
        name="Animal Average Overview",
        content=card,
    )

    #######################################
    #   Total event per animal   #
    #######################################

    df_plot = (
        df.groupby(["RFID"], observed=True)[["EVENT_COUNT", "DURATION"]]
        .sum()
        .reset_index()
    )

    figs = []
    figs.append(
        px.bar(
            df_plot,
            x="RFID",
            y="EVENT_COUNT",
            title=f"Total <i>{event_name}</i> number of events per animal",
            **plot_parameters,
        )
    )
    figs.append(
        px.bar(
            df_plot,
            x="RFID",
            y="DURATION",
            title=f"Total <i>{event_name}</i> events duration per animal",
            labels={"DURATION": "DURATION (min)"},
            **plot_parameters,
        )
    )

    report_description = f"""
    Total number of <i>{event_name}</i> event (EVENT_COUNT) and the sum of
    their duration in minutes (DURATION) for each animal (RFID).
    <br>
    This graph allows a visualization of the number of events each animal has
    done and the time spent in this event.<br>
    <br>
    <div style="color: #DE9BDE"><i>
    <b>Note:</b> Data for each animal is always valid.<br>
    However, if an event involves N animals simultaneously and is symmetrical
    (e.g., an 'Oral-oral contact' event), the total number of events is
    obtained by dividing the sum of the number of events for each animal by N.
    </i></div>
    """
    report_manager.add_multi_fig_report(
        name=f"Event overview",
        figures=figs,
        top_note=report_description,
        graph_datas=df_plot,
    )

    #######################################
    #   Mean and STD per animal   #
    #######################################

    figs = []

    df_plot = (
        df.groupby("RFID", observed=True)[["EVENT_COUNT", "DURATION"]]
        .agg(["mean", "std"])
        .reset_index()
    )
    df_plot.columns = [
        "RFID",
        "EVENT_COUNT_MEAN",
        "EVENT_COUNT_STD",
        "DURATION_MEAN",
        "DURATION_STD",
    ]

    label = f"EVENT_COUNT per bin ({int(
        df_constructor.binner.bin_size / df_constructor.binner.fps / 60
    )} min)"
    figs.append(
        px.bar(
            df_plot,
            x="RFID",
            y="EVENT_COUNT_MEAN",
            error_y="EVENT_COUNT_STD",
            error_y_minus=[0] * len(df_plot),
            title="Mean and Std of EVENT_COUNT per bin per RFID",
            labels={"EVENT_COUNT_MEAN": label},
            **plot_parameters,
        )
    )

    label = f"DURATION (min) per bin ({int(
        df_constructor.binner.bin_size / df_constructor.binner.fps / 60
    )} min)"
    figs.append(
        px.bar(
            df_plot,
            x="RFID",
            y="DURATION_MEAN",
            error_y="DURATION_STD",
            error_y_minus=[0] * len(df_plot),
            title="Mean and Std of DURATION per bin per RFID",
            labels={"DURATION_MEAN": label},
            **plot_parameters,
        )
    )

    report_title = "Event duration mean and standard deviation"
    report_description = f"""
    The mean of all <i>{event_name}</i> events duration (DURATION_MEAN) with
    the standard deviation (DURATION_STD) per animal (RFID).
    <br>
    This graph allows a visualization of the mean duration of one event for
    each animal as well as the variability of this duration.
    """
    report_manager.add_multi_fig_report(
        name=report_title,
        figures=figs,
        top_note=report_description,
        graph_datas=df_plot,
    )

    #######################################
    #   Event per hour of the day   #
    #######################################

    df_plot = df.copy()
    df_plot["DAYS"] = df_plot[TIME].apply(lambda x: x.day)
    df_plot["HOUR"] = df_plot[TIME].apply(lambda x: x.hour)

    nb_days_per_hour = []
    for h in range(24):
        nb_days_per_hour.append(
            df_plot[df_plot["HOUR"] == h]["DAYS"].nunique()
        )

    df_plot = (
        df_plot.groupby(["RFID", "HOUR"], observed=True)[
            ["EVENT_COUNT", "DURATION"]
        ]
        .sum()
        .reset_index()
        .sort_values(by="HOUR")
    )

    for rfid in df_plot["RFID"].unique():
        for h in df_plot[df_plot["RFID"] == rfid]["HOUR"].unique():
            df_plot.loc[
                (df_plot["RFID"] == rfid) & (df_plot["HOUR"] == h), "DAYS"
            ] = nb_days_per_hour[h]

    df_plot["EVENT_COUNT_PER_DAY"] = df_plot["EVENT_COUNT"] / df_plot["DAYS"]
    df_plot["DURATION_PER_DAY"] = df_plot["DURATION"] / df_plot["DAYS"]

    df_plot["HOUR"] = df_plot["HOUR"].astype(str) + "h"

    figs = []
    figs.append(
        px.line_polar(
            df_plot,
            r="EVENT_COUNT_PER_DAY",
            theta="HOUR",
            line_close=True,
            title="Hourly EVENT_COUNT_PER_DAY",
            **plot_parameters,
        )
    )
    last_tick = floor_power10(df_plot["EVENT_COUNT_PER_DAY"].max())
    if last_tick < 1:
        tick_label = f"{last_tick:.1f}"
    else:
        tick_label = str(int(last_tick))
    figs[-1].update_polars(
        radialaxis_tickvals=[last_tick], radialaxis_ticktext=[tick_label]
    )

    figs.append(
        px.line_polar(
            df_plot,
            r="DURATION_PER_DAY",
            theta="HOUR",
            line_close=True,
            title="Hourly DURATION_PER_DAY (min)",
            **plot_parameters,
        )
    )
    last_tick = floor_power10(df_plot["DURATION_PER_DAY"].max())
    if last_tick < 1:
        tick_label = f"{last_tick:.1f}"
    else:
        tick_label = str(int(last_tick))
    figs[-1].update_polars(
        radialaxis_tickvals=[last_tick], radialaxis_ticktext=[tick_label]
    )

    report_description = f"""
    Total number of <i>{event_name}</i> events and duration per animal and per
    hour of the day.
    
    Cumulated number (EVENT_COUNT_PER_DAY) and cumulated time
    (DURATION_PER_DAY) taken by <i>{event_name}</i> event for each animal
    (RFID) over each hour of the day divided by the numbers of times this hour
    occurs (DAYS).
    <br>
    This graph allows a visualization hours by hours of the <i>{event_name}</i>
    event for each animal.
    """
    report_manager.add_multi_fig_report(
        name=f"Event per hour of the day",
        figures=figs,
        top_note=report_description,
        max_fig_in_row=2,
        graph_datas=df_plot,
    )

    #######################################
    #   Event counts   #
    #######################################

    fig = px.line(
        df[MASK],
        x=TIME,
        y="EVENT_COUNT",
        title=f"EVENT_COUNT per animal over {TIME}",
        **plot_parameters,
    )
    fig = draw_nights(fig, **nights_parameters)

    report_title = f"Number of event per animal over time"
    report_description = f"""
    Number of <i>{event_name}</i> event (EVENT_COUNT) for each
    animal (RFID) over time ({TIME}) during the interval time window.
    <br>
    This graph allows a visualization of the time spent by each animal in this
    event over time.
    """

    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "EVENT_COUNT", "DURATION"]],
    )

    #######################################
    #   Event duration   #
    #######################################

    fig = px.line(
        df[MASK],
        x=TIME,
        y="DURATION",
        title=f"DURATION per animal over {TIME}",
        labels={"DURATION": "DURATION (min)"},
        **plot_parameters,
    )
    fig = draw_nights(fig, **nights_parameters)

    report_title = f"Number of event & event duration per animal over time"
    report_description = f"""
    Duration of <i>{event_name}</i> event (DURATION) for each
    animal (RFID) over time ({TIME}) during the interval time window.
    <br>
    This graph allows a visualization of the time spent by each animal in this
    event over time.
    """

    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "EVENT_COUNT", "DURATION"]],
    )

    #######################################
    #   TABLE   #
    #######################################
    report_manager.add_table_headers(name="complete table", df=df)

    #######################################
    #   Return   #
    #######################################
    return df
