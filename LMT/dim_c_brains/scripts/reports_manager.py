"""
@author: xmousset
"""

import os
import sys
import webbrowser
from pathlib import Path
from typing import Literal, List

import pandas as pd
import plotly.graph_objects as go

from dim_c_brains.res.report.Report import Report
from dim_c_brains.res.report.WebSite import WebSite


class HTMLReportManager:
    """
    A manager for creating, organizing, and exporting HTML reports with
    Plotly figures and tables.

    This class provides methods to add individual or multiple Plotly figures,
    tables, and custom HTML content as reports. Reports can be arranged in
    rows or grids, and optional notes can be included. The manager can
    generate a local HTML website containing all accumulated reports, using
    a specified template and asset folder structure.

    Main Features:
        - Add single or multiple Plotly figures or HTML blocks as reports.
        - Arrange figures in rows or grids for flexible layouts.
        - Add tables (from pandas DataFrames) and custom HTML titles/notes.
        - Generate a local HTML output website with all reports, using
          templates and assets.
    """

    @staticmethod
    def open_local_output(output_folder: Path):
        """Open the generated local HTML output in the default web browser."""
        if not (output_folder / "index.html").exists():
            print(
                """Error: index.html not found in the specified output folder.
                Please generate the local output first."""
            )
        else:
            webbrowser.open(str(output_folder / "index.html"))

    def __init__(self):
        """Initialize the HTMLReportManager."""
        self.reports = []
        self.exp_name = "main"
        self.html_param = {
            "full_html": False,
            "include_plotlyjs": "cdn",
            "config": {"displaylogo": False},
        }
        self.dimcbrains_path = Path(__file__).parent.parent

    def reports_creation_focus(self, exp_name: str = "main"):
        """Define where the new reports will be added. The main page is
        focused by default. If the input name is the same as an experiment
        that already exist, the new reports will be added after all the reports
        already created.
        """
        self.exp_name = exp_name

    def add_report(
        self,
        name: str,
        html_figure: go.Figure | str | None = None,
        top_note: str | None = None,
        graph_datas: pd.DataFrame | None = None,
    ):
        """
        Add a report to the `self.reports` list with the specified parameters.
        This method can accept a Plotly figure, an HTML string, or None for the
        report's figure. If a Plotly figure is provided, it is converted to
        HTML. Optionally, a note can be added above the figure, and a pandas
        DataFrame can be attached for download.

        Args:
            name (str): The name of the report.
            html_figure (go.Figure | str | None): A Plotly figure or HTML
                string to include in the report. If None, no figure is added.
            top_note (str | None): An optional note to include above the
                figure.
            graph_datas (pd.DataFrame | None): An optional pandas DataFrame
                containing data related to the report, which can be made
                available for download.
        """
        html = ""
        if top_note is not None:
            html += top_note + "<hr>"

        if html_figure is not None:
            if isinstance(html_figure, go.Figure):
                html += html_figure.to_html(**self.html_param)
            else:
                html += html_figure

        report = Report(name, html, experimentName=self.exp_name)

        if graph_datas is not None:
            report.setDownloadableContent("Download .xlsx", graph_datas)

        self.reports.append(report)

    def add_multi_fig_report(
        self,
        name: str,
        figures: List[go.Figure | str],
        top_note: str | None = None,
        max_fig_in_row: int | None = None,
        graph_datas: pd.DataFrame | None = None,
    ):
        """
        Add multiple Plotly figures as a single report, displayed in a matrix
        layout.

        Parameters
        ----------
        name : str
            The name of the report.
        figures : List[go.Figure | str]
            A list of Plotly figures or HTML strings to include in the report.
        note : str | None
            An optional note to include above the figures.
        max_fig_in_row : int | None
            Maximum number of figures to display in each row. If None, all
            figures will be displayed in a single row.
        """
        nb_fig = len(figures)
        html = ""

        if nb_fig == 0:
            return

        if max_fig_in_row is None:
            cols = nb_fig
            rows = 1
        else:
            cols = min(max_fig_in_row, nb_fig)
            rows = (nb_fig + cols - 1) // cols

        if top_note is not None:
            html += top_note + "<hr>"

        html += "<div class='container'>"
        for j in range(rows):
            html += "<div class='row'>"
            for i in range(cols):
                idx = j * cols + i
                if idx < nb_fig:
                    html += f"<div class='col-{12 // cols}'>"
                    figure = figures[idx]
                    if isinstance(figure, str):
                        html += figure
                    else:
                        html += figure.to_html(**self.html_param)
                    html += "</div>"
            html += "</div>"
        html += "</div>"

        report = Report(name, html, experimentName=self.exp_name)

        if graph_datas is not None:
            report.setDownloadableContent("Download .xlsx", graph_datas)

        self.reports.append(report)

    def add_title(
        self,
        name: str,
        content: str = "",
        style: Literal["primary", "success", "danger", "warning"] = "success",
    ):
        """Add a title block as a report."""
        report = Report(
            name,
            content,
            experimentName=self.exp_name,
            template="splitter.html",
            style=style,
        )
        self.reports.append(report)

    def add_card(
        self,
        name: str,
        content: str = "",
        style: Literal["primary", "success", "danger", "warning"] = "warning",
    ):
        """Add a card block as a report."""
        card_title = (
            "<div style='text-align: center;'>"
            "<strong>"
            "<span style='color: black;'>"
            f"{name}"
            "</strong>"
            "</span>"
            "</div>"
        )
        card_content = f"<span style='color: black;'>" f"{content}" "</span>"
        report = Report(
            card_title,
            card_content,
            experimentName=self.exp_name,
            template="miniCard.html",
            style=style,
        )
        self.reports.append(report)

    def add_table(self, name: str, df: pd.DataFrame):
        """Add a table report from a pandas DataFrame."""
        report = Report(
            name,
            df,
            experimentName=self.exp_name,
            template="table.html",
        )
        report.setDownloadableContent("Download .xlsx", df)
        self.reports.append(report)

    def generate_local_output(
        self,
        output_folder: Path,
    ):
        """Generate an HTML output locally from the accumulated reports."""
        output_folder.mkdir(parents=True, exist_ok=True)
        webSite = WebSite(
            templateFolder=str(self.dimcbrains_path / "res" / "template"),
            outFolder=str(output_folder.absolute()) + "/",
            defaultWebSiteFolder=str(self.dimcbrains_path / "res" / "assets"),
            passFile="None",
        )

        webSite.initWebSiteOutFolder()

        for report in self.reports:
            webSite.addReport(report)

        webSite.generateWebSite()
        print(
            "Local output generated at:\n" + str(output_folder / "index.html")
        )
