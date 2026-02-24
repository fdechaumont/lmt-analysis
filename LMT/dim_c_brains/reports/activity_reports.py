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
from dim_c_brains.reports.overview_reports import get_activity_card


def generic_reports(
    report_manager: HTMLReportManager,
    df_constructor: DataFrameConstructor,
    **kwargs,
):
    """Analyse mice activity and creates a generic dataframe using the given
    `DataFrameConstructor` and construct all the generic reports into the given
    `HTMLReportManager` and returning the generated dataframe.

    Other Parameters
    ----------------
    time : str, optional
        The time column to use (i.e. "START_TIME" or "END_TIME",
        default: "START_TIME").
    night_begin : int, optional
        The hour when the night begins (default: 20).
    night_duration : int, optional
        The duration of the night in hours (default: 12).
    filter_flickering : bool, optional
        Whether to filter flickering activity (default: False).
    filter_stop : bool, optional
        Whether to filter stop activity (default: False).
    first_value_in_graph : bool, optional
        Whether to ignore the first value in plots. It impacts the
        rendering of columns graphs and so is ignored by default
        (default: True).
    """

    report_manager.reports_creation_focus("Activity")
    df = df_constructor.process_activity(
        kwargs.get("filter_flickering", False),
        kwargs.get("filter_stop", False),
    )

    if df is None:
        report_manager.add_title(
            name="Analysis of mice activity",
            content="""
            No data available for the selected time interval. Please adjust
            the processing limits or check the database connection.""",
        )
        return None

    #######################################
    #   Constants & Parameters   #
    #######################################

    TIME: str = kwargs.get("time", "START_TIME")

    NB_ANIMALS = df["RFID"].nunique()

    exp_start_time, exp_end_time = df_constructor.get_processing_limits("TIME")
    NB_DAYS = (exp_end_time - exp_start_time).total_seconds() / 3600 / 24

    if kwargs.get("first_value_in_graph", True):
        MASK = df["START_FRAME"] != df["START_FRAME"].iloc[0]
    else:
        MASK = df.index == df.index

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
        name=f"Analysis of mice activity",
        content=f"""
        This section presents the analysis of mice Activity recorded in the
        dataset. You can download the underlying data used for the plots
        in Excel format by clicking on the '<i>Download .xlsx</i>' link on the
        top-right hand corner.""",
    )

    report_manager.add_card(
        name="Time interval unit",
        content=f"""
        Calculated time bin is {df_constructor.binner.bin_size} frames.<br>
        It corresponds to {df_constructor.binner.bin_size / 30 / 60} minutes.
        """,
    )
    report_manager.add_card(
        name="Distance unit",
        content="All distances are in centimeters (<i>cm</i>).",
    )
    report_manager.add_card(
        name="Speed unit",
        content="All speeds are in centimeters per second (<i>cm/s</i>).",
    )

    #######################################
    #   Activity overview card   #
    #######################################

    card = get_activity_card(df, NB_ANIMALS, NB_DAYS, **kwargs)

    report_manager.add_card(
        name="Animal Average Overview",
        content=card,
    )

    #######################################
    #   Distance   #
    #######################################

    fig = px.line(
        df[MASK],
        TIME,
        "DISTANCE",
        labels={"DISTANCE": "DISTANCE (<i>cm</i>)"},
        **plot_parameters,
    )
    fig = draw_nights(fig, **nights_parameters)

    report_title = f"Total distance travelled"
    report_description = f"""
    This graph shows the total distance in centimeters (DISTANCE) travelled by
    each animal (RFID) over time ({TIME}) during the interval time window.
    <br>
    This graph shows the locomotor activity of each animal
    over time.
    """
    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "DISTANCE"]],
    )

    #######################################
    #   Event: Stop   #
    #######################################

    fig = px.line(
        df[MASK],
        TIME,
        "STOP_DURATION",
        labels={"STOP_DURATION": "STOP_DURATION (<i>min</i>)"},
        **plot_parameters,
    )
    fig = draw_nights(fig, **nights_parameters)

    report_title = f"Stop duration"
    report_description = f"""
    Duration in minutes of event <i>Stop</i> (STOP_DURATION) by each animal (RFID) over time
    ({TIME}) during the interval time window.
    <br>
    This graph shows the time spent immobile by each animal
    over time.
    """
    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "STOP_DURATION"]],
    )

    #######################################
    #   Event: Move   #
    #######################################

    fig = px.line(
        df[MASK],
        TIME,
        "MOVE_DURATION",
        labels={"MOVE_DURATION": "MOVE_DURATION (<i>min</i>)"},
        **plot_parameters,
    )
    fig = draw_nights(fig, **nights_parameters)

    report_title = f"Move duration"
    report_description = f"""
    Duration in minutes of event <i>Move</i> (MOVE_DURATION) by each animal
    (RFID) over time ({TIME}) during the interval time window.
    <br>
    This graph shows the time spent moving by each animal
    over time.
    """
    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "MOVE_DURATION"]],
    )

    #######################################
    #   Event: Undetected   #
    #######################################

    fig = px.line(
        df[MASK],
        TIME,
        "UNDETECTED_DURATION",
        labels={"UNDETECTED_DURATION": "UNDETECTED_DURATION (<i>min</i>)"},
        **plot_parameters,
    )
    fig = draw_nights(fig, **nights_parameters)

    report_title = f"Undetected duration"
    report_description = f"""
    Duration in minutes of event <i>Undetected</i> (UNDETECTED_DURATION) by
    each animal (RFID) over time ({TIME}) during the interval time window.
    <br>
    This graph shows, over time, the duration when each animal was not detected
    by the LMT.
    """
    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "UNDETECTED_DURATION"]],
    )

    #######################################
    #   Movement and stop duration per hour of the day   #
    #######################################
    df_plot = df.copy()
    df_plot["HOUR"] = df_plot[TIME].apply(lambda x: x.hour)
    df_plot = (
        df_plot.groupby(["RFID", "HOUR"], observed=True)[
            ["MOVE_DURATION", "STOP_DURATION"]
        ]
        .sum()
        .reset_index()
        .sort_values(by="HOUR")
    )
    df_plot["HOUR"] = df_plot["HOUR"].astype(str) + "h"

    figs = []
    figs.append(
        px.line_polar(
            df_plot,
            r="MOVE_DURATION",
            theta="HOUR",
            line_close=True,
            title="Hourly MOVE_DURATION (<i>min</i>)",
            **plot_parameters,
        )
    )
    figs.append(
        px.line_polar(
            df_plot,
            r="STOP_DURATION",
            theta="HOUR",
            line_close=True,
            title="Hourly STOP_DURATION (<i>min</i>)",
            **plot_parameters,
        )
    )

    report_description = f"""
    Cumulated time taken by <i>Stop</i> events (STOP_DURATION) by each animal
    (RFID) over each hour of the day.
    <br>
    The opposite is the time spent moving (MOVE_DURATION) in minutes. It is
    calculated as the interval time window minus STOP_DURATION.
    <br>
    This graph shows the activity of each animal hours by
    hours.
    """
    report_manager.add_multi_fig_report(
        name=f"Movement and stop duration per hour of the day",
        figures=figs,
        top_note=report_description,
        max_fig_in_row=2,
        graph_datas=df_plot,
    )

    #######################################
    #   Cumulative speeds   #
    #######################################

    # fig = px.bar(
    #     df[MASK],
    #     TIME,
    #     "SPEED_SUM",
    #     color="RFID",
    #     labels={"SPEED_SUM": "SPEED_SUM (<i>cm/s</i>)"},
    # )
    # fig = draw_nights(fig, **nights_parameters)

    # report_title = f"Cumulative speed"
    # report_description = f"""
    # Cumulated speed (SPEED_SUM) of each animal (RFID) over time ({TIME})
    # during the interval time window.
    # <br>
    # This graph shows how much the activity of each animal
    # hours by hours.
    # """
    # report_manager.add_report(
    #     name=report_title,
    #     figure=fig,
    #     note=report_description,
    #     graph_datas=df[["RFID", TIME, "SPEED_SUM"]],
    # )

    #######################################
    #   Speed mean and min max   #
    #######################################

    fig = line_with_shade(
        df[MASK],
        TIME,
        "SPEED_MEAN",
        y_std_col="SPEED_STD",
        # y_min_col="SPEED_MIN",
        # y_max_col="SPEED_MAX",
        **plot_parameters,
    )
    fig.update_yaxes(range=[0, None])
    fig.update_layout(yaxis_title="SPEED_MEAN (<i>cm/s</i>)")
    fig = draw_nights(fig, **nights_parameters)

    # description for STD
    report_title = f"Mean speed with std"
    report_description = f"""
    Mean speed (SPEED_MEAN) with the standard deviation (SPEED_STD) for each
    animal (RFID) over time ({TIME}).
    """

    # description for min max
    # report_title = f"Mean speed with min and max"
    # report_description = f"""
    # Mean speed (SPEED_MEAN) with the minimum (SPEED_MIN) and maximum
    # (SPEED_MAX) speeds for each animal (RFID) over time ({TIME}).
    # """

    report_manager.add_report(
        name=report_title,
        html_figure=fig,
        top_note=report_description,
        graph_datas=df[["RFID", TIME, "SPEED_MEAN", "SPEED_STD"]],
    )

    #######################################
    #   TABLE   #
    #######################################
    report_manager.add_table_headers(name="complete table", df=df)

    #######################################
    #   Return   #
    #######################################
    return df
