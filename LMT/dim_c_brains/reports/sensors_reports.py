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


def generic_reports(
    report_manager: HTMLReportManager,
    df_constructor: DataFrameConstructor,
    **kwargs,
):
    """Get all sensors datas in a dataframe using the given
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

    report_manager.reports_creation_focus("Sensors")
    df = df_constructor.process_sensors()

    if df is None:
        print("No sensors data available")
        report_manager.add_report(
            name="Sensors data not available",
            html_figure="""
            No sensors data available in this dataset.
            """,
        )
        return None

    #######################################
    #   Constants & Parameters   #
    #######################################

    TIME = kwargs.get("time", "START_TIME")

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

    sensors = [
        "TEMPERATURE",
        "HUMIDITY",
        "SOUND",
        "LIGHTVISIBLE",
        "LIGHTVISIBLEANDIR",
    ]
    sensors_labels = [
        "Temperature",
        "Humidity",
        "Sound",
        "Light visible",
        "Light visible + IR",
    ]
    units = [
        "°C",
        "%",
        "?",
        "?",
        "?",
    ]

    #######################################
    #   Titles   #
    #######################################

    report_manager.add_title(
        name=f"Sensors data visualization",
        content=f"""
        This section presents the visualization of the sensors data recorded in
        the dataset. All sensors data can be downloaded in Excel format by
        clicking on the '<i>Download .xlsx</i>' link on the top-right hand
        corner of the last report (<i>complete table</i>).""",
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
        name="Sensors units",
        content="?",
    )

    #######################################
    #   Sensors overview card   #
    #######################################

    card = """<div style="flex: 0 0 320px; min-width: 220px;
    max-width: 400px;"> <div style="margin:0; padding:0;">
    """
    for sensor, label, unit in zip(sensors, sensors_labels, units):
        if (
            sensor + "_MEAN" not in df.columns
            or df[sensor + "_MEAN"].isnull().all()
        ):
            card += (
                f"<p style='margin: 0.5em 0;'>{label} data not available</p>"
            )
        else:
            mean = round(df[sensor + "_MEAN"].mean(), 2)
            std = round(df[sensor + "_MEAN"].std(), 2)
            card += (
                f"<p style='margin: 0.5em 0;'>{label} : "
                f"<strong>{mean}</strong> "
                f"<span>&plusmn;</span> {std} {unit}</p>"
            )
    card += "</div></div>"

    report_manager.add_card(
        name="Sensors",
        content=card,
    )

    #######################################
    #   Sensors plots   #
    #######################################

    for sensor, sensor_label, unit in zip(sensors, sensors_labels, units):

        mean_col = f"{sensor}_MEAN"
        min_col = f"{sensor}_MIN"
        max_col = f"{sensor}_MAX"

        if mean_col in df.columns:
            fig = line_with_shade(
                df[MASK],
                TIME,
                mean_col,
                y_min_col=min_col,
                y_max_col=max_col,
            )
            fig = draw_nights(fig, **nights_parameters)

            fig.update_layout(
                title=f"{sensor_label} over time",
                yaxis_title=f"{sensor_label} ({unit})",
                xaxis_title=f"Time ({TIME})",
            )

            report_title = f"{sensor_label} mean with min and max"
            report_description = f"""
            {sensor_label} mean ({mean_col}) with the minimum and maximum as
            the shaded area ({min_col}, {max_col}) over time ({TIME}).<br>
            """
            if sensor == "LIGHTVISIBLE":
                report_description += """
                This graph allows a visualization of the Day and Night cycle
                between what is expected (grey bands) and what the sensors
                recorded (line with shaded area).
                """

            report_manager.add_report(
                name=report_title,
                html_figure=fig,
                top_note=report_description,
                graph_datas=df[
                    [
                        TIME,
                        "END_TIME",
                        mean_col,
                        min_col,
                        max_col,
                    ]
                ],
            )
        else:
            report_manager.add_report(
                name=f"{sensor_label} data not available",
                html_figure=f"""
                No data available for {sensor} sensor in this dataset.
                """,
            )

    #######################################
    #   TABLE   #
    #######################################
    report_manager.add_table_headers(name="complete table", df=df)

    #######################################
    #   Return   #
    #######################################
    return df
