"""
@author: xmousset
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime

#######################################
#   APP Creation Parameters   #
#######################################
APP_CREATION = False
APP_VERSION = ["1.0.1", "1.0.0"]  # decreasing orders
APP_RELEASE = ["2026-02-27", "2026-02-23"]  # decreasing orders
APP_ICON = Path(__file__).parent / "res" / "lmt_eye_icon.png"
# command for executable creation (run in terminal at project root):
# pyinstaller -p LMT --onefile --icon=LMT/dim_c_brains/res/lmt_eye_icon.png --add-data "LMT/dim_c_brains/res/template;dim_c_brains/res/template" --add-data "LMT/dim_c_brains/res/assets;dim_c_brains/res/assets" LMT/dim_c_brains/lmt_eye_app.py

if APP_CREATION:
    print("Starting LMT-EYE...")
else:
    # ADD LMT FOLDER TO PYTHON PATH
    lmt_analysis_path = Path(__file__).parent.parent
    sys.path.append(str(lmt_analysis_path))

import sqlite3
import numpy as np
import pandas as pd

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dim_c_brains.scripts.events_and_modules import ALL_EVENTS
from dim_c_brains.lmt_eye_data_analysis import LMTEYEDataAnalyzer
from dim_c_brains.lmt_eye_settings import LMTEYESettings
from dim_c_brains.scripts.pyqt6_tools import YesNoQuestion, get_btn_style

from lmtanalysis.Animal import AnimalType


class AnalysisAppWindow(QWidget):
    """Main application window for LMT-EYE."""

    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.setWindowTitle("LMT-EYE - v" + APP_VERSION[0])
        self.setFixedSize(550, 400)
        self.setWindowIcon(QIcon(str(APP_ICON)))

        self.database_path = None

        self._init_ui()

    def _init_ui(self):
        """Initialize the UI elements of the main application window."""
        main_layout = QVBoxLayout()

        #######################################
        #   Help button   #
        #######################################
        btn_style = get_btn_style(
            size=18,
            bold=True,
            txt_color="#FFFFFF",
            bg_color="#EA2A94",
            radius=15,
        )
        help_btn = QPushButton("?")
        help_btn.setFixedSize(42, 42)
        help_btn.setStyleSheet(btn_style)
        help_btn.setToolTip("Help / About")
        help_btn.clicked.connect(self.show_help_dialog)

        help_row = QHBoxLayout()
        help_row.addStretch(1)
        help_row.addWidget(help_btn)
        main_layout.addLayout(help_row)

        #######################################
        #   Database informations   #
        #######################################
        self.info_label = QLabel()
        self.info_label.setTextFormat(Qt.TextFormat.RichText)
        self.info_label.setText("<b>No loaded database.</b>")

        db_info_row = QHBoxLayout()
        db_info_row.addWidget(self.info_label)
        main_layout.addLayout(db_info_row)

        #######################################
        #   Buttons row   #
        #######################################

        # database button
        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        self.load_db_btn = QPushButton("Load Database")
        self.load_db_btn.setStyleSheet(btn_style)
        self.load_db_btn.setFixedSize(150, 50)
        self.load_db_btn.clicked.connect(self.on_load_db)

        btn_style = get_btn_style(size=15, bold=True)

        # update animals information button
        self.update_info_btn = QPushButton("Animals Infos")
        self.update_info_btn.setStyleSheet(btn_style)
        self.update_info_btn.setFixedSize(150, 50)
        self.update_info_btn.clicked.connect(self.on_update_info)

        # continue button
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.setStyleSheet(btn_style)
        self.continue_btn.setFixedSize(150, 50)
        self.continue_btn.clicked.connect(self.on_continue)

        # row layout
        buttons_row = QHBoxLayout()
        buttons_row.addStretch(1)
        buttons_row.addWidget(self.load_db_btn)
        buttons_row.addWidget(self.update_info_btn)
        buttons_row.addWidget(self.continue_btn)
        buttons_row.addStretch(1)

        main_layout.addLayout(buttons_row)

        self.setLayout(main_layout)

    def update_database_info(self):
        """Update database information displayed in the main window."""
        infos = {}
        if self.database_path is not None:
            t_format = "%Y %B - %A %d - %H:%M"
            infos = LMTEYEDataAnalyzer.get_informations(self.database_path)

            local_time = datetime.now().astimezone()
            utc_offset = local_time.utcoffset()
            utc_offset_name = local_time.tzname()
            if utc_offset is None:
                print("Warning: UTC offset is None, setting to 0.")
                utc_offset = pd.Timedelta(0)
                utc_offset_str = "?"
            else:
                utc_hours = utc_offset.total_seconds() / 3600
                if utc_hours == int(utc_hours):
                    utc_offset_str = f"{int(utc_hours):+.0f}"
                elif (utc_hours * 10) == int(utc_hours * 10):
                    utc_offset_str = f"{utc_hours:+.1f}"
                else:
                    utc_offset_str = f"{utc_hours:+.2f}"

            start_time = (infos["start_time"] + utc_offset).strftime(t_format)
            end_time = (infos["end_time"] + utc_offset).strftime(t_format)
            d = infos["duration"].days
            h = infos["duration"].seconds // 3600
            m = (infos["duration"].seconds // 60) % 60
            info_html = f"""
                <table style='font-size:13px;'>
                <tr>
                    <td><b>Database:</b></td>
                    <td>{infos["database_name"]}</td>
                </tr>
                <tr>
                    <td><b>Animals:</b></td>
                    <td>{infos["n_animals"]}</td>
                </tr>
                <tr>
                    <td><b>Start:</b></td>
                    <td>{start_time}</td>
                </tr>
                <tr>
                    <td><b>End:</b></td>
                    <td>{end_time}</td>
                </tr>
                <tr>
                    <td colspan="2" style="color: gray; font-family: Calibri;">
                        <center><i>
                            <span>&#11169;</span>&nbsp;
                            UTC{utc_offset_str} - {utc_offset_name}
                        </i></center>
                    </td>
                </tr>
                <tr>
                    <td><b>Duration:</b></td>
                    <td>{d} days, {h} hours and {m} minutes</td>
                </tr>
                <tr>
                    <td><b>FPS:</b></td>
                    <td>{infos["fps"]:.1f}</td>
                </tr>
                </table>
            """
            self.info_label.setText(info_html)
        else:
            info_html = f"""
                <table style='font-size:13px;'>
                <tr><td><b>Database:</b></td><td>No loaded database.</td></tr>
                </table>
            """

        self.info_label.setText(info_html)

    def on_load_db(self):
        """Launches a file dialog for loading database."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SQLite file",
            "",
            "SQLite files (*.sqlite);;All files (*)",
        )
        if not file_path:
            return
        self.database_path = Path(file_path)
        self.update_database_info()

        btn_style = get_btn_style(size=15, bold=True)
        self.load_db_btn.setStyleSheet(btn_style)

        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        self.continue_btn.setStyleSheet(btn_style)
        self.update_info_btn.setStyleSheet(btn_style)

    def warning_message_load_database(self):
        """Check if a database is loaded, and show a warning if not."""
        QMessageBox.warning(
            self,
            "No Database",
            "Please load a database before anything.",
        )

    def on_update_info(self):
        """Update animals information in database."""
        if self.database_path is None:
            self.warning_message_load_database()
            return

        UpdateDatabaseInfo(self, self.database_path).exec()

    def on_continue(self):
        """Rebuild database then analyse it."""
        if self.database_path is None:
            self.warning_message_load_database()
            return

        dlg = SettingsWindow(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            settings = dlg.settings
        else:
            print("Process cancelled.")
            return

        msg = """
        <p align="justify">
        The analysis process is about to start. This may take a while
        depending on the database size and your computer performance.<br><br>
        Please, do not close the logs window and wait until the analysis is
        finished. When finishded, the app window will come back and it will
        display the following message:
        </p>
        <p style="text-align:center;"><b>*** PROCESS FINISHED ***</b></p>
        """

        QMessageBox.information(
            self,
            "Process Starting",
            msg,
        )

        self.hide()  # Hide main window during processing

        analyzer = LMTEYEDataAnalyzer(self.database_path, settings)
        print("Rebuilding database...")
        analyzer.rebuild_database()
        print("Rebuild finished.")
        print("Starting analysis...")
        analyzer.run_analysis()
        print("Analysis finished.")
        print("\n*** PROCESS FINISHED ***\n")

        print(f"Process for {self.database_path.stem} finished.")

        self.show()  # Show main window again after processing

        if analyzer.settings.output_folder is None:
            raise ValueError(
                "Output folder is not defined after running analysis. "
                "This should not happen."
            )
        index_file = analyzer.settings.output_folder / "index.html"
        if not index_file.is_file():
            print(f"Warning: Analysis output file '{index_file}' not found.")
            return

        dlg = YesNoQuestion(self, "Open analysis ?")
        if dlg.exec():
            print(f"Opening {str(index_file)}.")
            analyzer.open_analysis_output()

        return analyzer

    def show_help_dialog(self):
        info_msg = f"""
            <b>LMT-EYE</b> - <i>Explore Your Experiments !</i><br>
            <br>
            Version: {APP_VERSION[0]}<br>
            Release date: {APP_RELEASE[0]}<br>
            Github: <a href='https://github.com/xmousset/lmt-analysis'>
            LMT-EYE repository</a><br>
            <br>
            To seek for help, visit LMT website:<br>
            <a href='https://micecraft.org/lmt/'>
            https://micecraft.org/lmt/</a><br>
            <br>
            You can also go on the LMT Discord server to ask LMT creators and
            other users about your problems to have a quick answer:<br>
            <a href='https://discord.com/invite/zWDHNf9eHM'>
            Join LMT Discord server</a>
        """
        dlg = QDialog(self)
        dlg.setWindowTitle("Help")
        dlg.setFixedWidth(300)
        layout = QVBoxLayout(dlg)
        label = QLabel()
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setText(info_msg)
        label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        layout.addWidget(label)
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn_box.accepted.connect(dlg.accept)
        layout.addWidget(btn_box)
        dlg.exec()


class SettingsWindow(QDialog):
    """Dialog to edit LMT-EYE settings."""

    if APP_CREATION:
        SAVING_PATH = Path.home() / "documents" / "LMT-EYE_settings"
    else:
        SAVING_PATH = Path(__file__).parent / "res" / "LMT-EYE_settings"
    SAVING_PATH.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_default_settings():
        """Load default settings if available."""

        settings = LMTEYESettings()

        default_path = SettingsWindow.SAVING_PATH / "default_settings.json"

        if default_path.is_file():
            settings.load(default_path)
        else:
            print("Warning: 'default_settings.json' not found.")

        return settings

    def __init__(self, parent: QWidget | None):
        """Initialize the settings window by loading default settings."""
        super().__init__(parent)
        self.setWindowTitle("LMT-EYE - Settings")

        self.settings = self.load_default_settings()
        self._init_ui()

    def _init_ui(self):
        form = QFormLayout()

        #######################################
        #   Output folder   #
        #######################################

        # output_folder
        if self.settings.output_folder is None:
            output_text = ""
        else:
            output_text = str(self.settings.output_folder)

        self.output_folder_edit = QLineEdit(output_text)
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setPlaceholderText(
            "same folder as database by default"
        )
        self.output_folder_edit.setToolTip(
            "Folder where analysis results will be saved."
        )
        out_btn = QPushButton("Browse")
        btn_style = get_btn_style()
        out_btn.setStyleSheet(btn_style)
        out_btn.setFixedWidth(80)
        out_btn.clicked.connect(self.select_output_folder)

        out_row = QHBoxLayout()
        out_row.addWidget(self.output_folder_edit)
        out_row.addWidget(out_btn)

        form.addRow("Output Folder", out_row)

        #######################################
        #   Animal Type   #
        #######################################

        # animal_type
        self.animal_type_box = QComboBox()
        self.animal_type_box.setToolTip(
            "Type of animals used in the experiment."
        )
        options = [animal_type.name for animal_type in AnimalType]
        self.animal_type_box.addItems(options)
        current_type = self.settings.animal_type.name
        if current_type in options:
            self.animal_type_box.setCurrentText(current_type)
        else:
            print(f"Animal type '{current_type}' is not available.")
            self.animal_type_box.setCurrentText("ERROR")

        # row layout
        animal_type_row = QHBoxLayout()
        animal_type_row.addWidget(self.animal_type_box)
        animal_type_row.addStretch(1)

        form.addRow("Animal type", animal_type_row)
        form.addRow(self.Qhline())

        #######################################
        #   EVENTS   #
        #######################################

        # events (known)
        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        self.select_events_btn = QPushButton("Select Events")
        self.select_events_btn.setToolTip(
            "Select events to rebuild and analyse in the analysis process."
        )
        self.select_events_btn.setStyleSheet(btn_style)
        self.select_events_btn.setFixedWidth(150)
        self.select_events_btn.clicked.connect(self.on_select_events)

        # events (custom)
        self.custom_event_edit = QLineEdit()
        self.custom_event_edit.setPlaceholderText("no custom events")
        self.custom_event_edit.setToolTip(
            "Enter custom event names to be included in the analysis. "
            "Separate multiple events with commas.\n"
            "(e.g.: Event1, Event2, Event3)"
        )

        # rebuild_events
        self.rebuild_box = QCheckBox()
        self.rebuild_box.setToolTip(
            "Wether to rebuild all selected events in the database before "
            "analysis (Checked)\n or to rebuild only the events that does not "
            "exists in the database (Unchecked).\n Unchecked is faster."
        )
        self.rebuild_box.setChecked(self.settings.rebuild_events)

        # rows layout
        events_row = QHBoxLayout()
        events_row.addStretch(4)
        events_row.addWidget(self.select_events_btn)
        events_row.addStretch(3)
        events_row.addWidget(QLabel("Rebuild:"))
        events_row.addWidget(self.rebuild_box)

        custom_row = QHBoxLayout()
        custom_row.addWidget(self.custom_event_edit)

        form.addRow(events_row)
        form.addRow("Custom events:", custom_row)
        form.addRow(self.Qhline())

        #######################################
        #   ANALYSIS FILTERS   #
        #######################################

        # filter_flickering
        self.flickering_cb = QCheckBox()
        self.flickering_cb.setToolTip(
            "Whether to filter the 'Flickering' event for animal activity.\n"
            "If enabled, all frames containing a 'Flickering' event will be "
            "excluded from the activity analysis."
        )
        self.flickering_cb.setChecked(self.settings.filter_flickering)

        # filter_stop
        self.stop_cb = QCheckBox()
        self.stop_cb.setToolTip(
            "Whether to filter the 'Stop' event for animal activity.\n"
            "If enabled, all frames containing a 'Stop' event will be "
            "excluded from the activity analysis."
        )
        self.stop_cb.setChecked(self.settings.filter_stop)

        # row layout
        filters_row = QHBoxLayout()
        filters_row.addWidget(QLabel("Flickering:"))
        filters_row.addWidget(self.flickering_cb)
        filters_row.addStretch(1)
        filters_row.addWidget(QLabel("Stop:"))
        filters_row.addWidget(self.stop_cb)
        filters_row.addStretch(1)

        form.addRow("Filters", filters_row)
        form.addRow(self.Qhline())

        #######################################
        #   TIME, PROCESSING and FPS   #
        #######################################

        # time_window (frames and minutes)
        self.time_window_frames = QSpinBox()
        self.time_window_frames.setToolTip(
            "Defines the binning of datas for the analysis (in frames)."
        )
        self.time_window_frames.setRange(1, 100_000_000)
        self.time_window_frames.setValue(self.settings.time_window)

        self.time_window_minutes = QDoubleSpinBox()
        self.time_window_minutes.setToolTip(
            "Defines the binning of datas for the analysis (in minutes)."
        )
        self.time_window_minutes.setDecimals(0)
        self.time_window_minutes.setRange(0, 100_000)
        self.time_window_minutes.setValue(
            int(self.settings.time_window / (self.settings.fps * 60))
        )

        # processing_window (frames and minutes)
        self.process_window_frames = QSpinBox()
        self.process_window_frames.setToolTip(
            "Defines the time window to consider for each processing step "
            "(in frames). Useful if the analysis is very long and needs to "
            "be processed in chunks.\n"
            "Do not impact analysis results."
        )
        self.process_window_frames.setRange(1, 100_000_000)
        self.process_window_frames.setValue(self.settings.processing_window)

        self.process_window_hours = QDoubleSpinBox()
        self.process_window_hours.setToolTip(
            "Defines the time window to consider for each processing step "
            "(in hours). Useful if the analysis is very long and needs to "
            "be processed in chunks.\n"
            "Do not impact analysis results."
        )
        self.process_window_hours.setDecimals(0)
        self.process_window_hours.setRange(0, 10_000)
        self.process_window_hours.setValue(
            int(
                self.settings.processing_window / (self.settings.fps * 60 * 60)
            )
        )

        # fps
        self.fps_spin = QSpinBox()
        self.fps_spin.setToolTip(
            "Frames per second of the recording.\n"
            "DO NOT MODIFY UNLESS YOU KNOW WHAT YOU ARE DOING."
        )
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(self.settings.fps)
        self.fps_spin.setMinimumWidth(75)

        # updates frames when times are changed, and vice versa
        self.time_window_frames.valueChanged.connect(
            self._on_time_frames_changed
        )
        self.time_window_minutes.valueChanged.connect(
            self._on_time_minutes_changed
        )
        self.process_window_frames.valueChanged.connect(
            self._on_process_frames_changed
        )
        self.process_window_hours.valueChanged.connect(
            self._on_process_hours_changed
        )
        self.fps_spin.valueChanged.connect(self._on_fps_changed)

        # layout for time, processing and fps
        time_row = QHBoxLayout()
        time_row.addStretch(1)
        time_row.addWidget(QLabel("Frames:"))
        time_row.addWidget(self.time_window_frames)
        time_row.addStretch(1)
        time_row.addWidget(QLabel("Minutes:"))
        time_row.addWidget(self.time_window_minutes)
        time_row.addStretch(1)
        form.addRow("Binning", time_row)

        proc_row = QHBoxLayout()
        proc_row.addStretch(1)
        proc_row.addWidget(QLabel("Frames:"))
        proc_row.addWidget(self.process_window_frames)
        proc_row.addStretch(1)
        proc_row.addWidget(QLabel("Hours:"))
        proc_row.addWidget(self.process_window_hours)
        proc_row.addStretch(1)
        form.addRow("Processing", proc_row)

        fps_row = QHBoxLayout()
        fps_row.addStretch(1)
        fps_row.addWidget(QLabel("FPS:"))
        fps_row.addWidget(self.fps_spin)
        fps_row.addStretch(1)
        form.addRow("", fps_row)

        form.addRow(self.Qhline())

        #######################################
        #   NIGHT TIME   #
        #######################################
        # night_begin
        self.night_begin_spin = QSpinBox()
        self.night_begin_spin.setToolTip(
            "Define when the night cycle began (in hours, 0-23).\n"
            "Only used to display a shadow on graphs during night hours."
        )
        self.night_begin_spin.setRange(0, 23)
        self.night_begin_spin.setValue(self.settings.night_begin)
        self.night_begin_spin.setMinimumWidth(75)

        # night_duration
        self.night_duration_spin = QSpinBox()
        self.night_duration_spin.setToolTip(
            "Define the night cycle duration (in hours, 0-24).\n"
            "Only used to display a shadow on graphs during night hours."
        )
        self.night_duration_spin.setRange(0, 24)
        self.night_duration_spin.setValue(self.settings.night_duration)
        self.night_duration_spin.setMinimumWidth(75)

        # night end (calculated)
        self.night_end_label = QLabel()

        # connect signals to update night end
        self.night_begin_spin.valueChanged.connect(self._evaluate_night_end)
        self.night_duration_spin.valueChanged.connect(self._evaluate_night_end)
        self._evaluate_night_end()

        # row layout
        night_row = QHBoxLayout()
        night_row.addStretch(1)
        night_row.addWidget(QLabel("Begin (h):"))
        night_row.addWidget(self.night_begin_spin)
        night_row.addStretch(1)
        night_row.addWidget(QLabel("Duration (h):"))
        night_row.addWidget(self.night_duration_spin)
        night_row.addStretch(1)
        night_row.addWidget(self.night_end_label)
        night_row.addStretch(1)

        form.addRow("Nights", night_row)

        #######################################
        #   UTC TIME ZONE   #
        #######################################
        # UTC_offset
        self.utc_offset_spin = QDoubleSpinBox()
        self.utc_offset_spin.setToolTip(
            "Define the UTC offset in hours for correct timezone conversion.\n"
            "For example, +1 for Paris, +9 for Tokyo or +5.75 for Kathmandu."
        )
        self.utc_offset_spin.setRange(-12.0, 14.0)
        self.utc_offset_spin.setValue(self.settings.UTC_offset)
        self.utc_offset_spin.setMinimumWidth(75)

        utc_row = QHBoxLayout()
        utc_row.addStretch(1)
        utc_row.addWidget(QLabel("UTC offset (h):"))
        utc_row.addWidget(self.utc_offset_spin)
        utc_row.addStretch(1)

        form.addRow("Time Zone", utc_row)
        form.addRow(self.Qhline())

        #######################################
        #   ANALYSIS LIMITS (start, end)   #
        #######################################

        # processing_limits (start)
        if self.settings.processing_limits[0] is None:
            start = None
        elif isinstance(self.settings.processing_limits[0], pd.Timestamp):
            start = self.settings.processing_limits[0].isoformat(
                sep=" ", timespec="seconds"
            )
        else:
            start = str(self.settings.processing_limits[0])
        self.start_edit = QLineEdit(start)
        self.start_edit.setToolTip(
            "Can be either a FRAMENUMBER (integer) "
            "or a TIMESTAMP (YYYY-MM-DD HH:MM:SS)"
        )
        self.start_edit.setPlaceholderText("first frame")
        self.start_edit.setMinimumHeight(30)

        # processing_limits (end)
        if self.settings.processing_limits[1] is None:
            end = None
        elif isinstance(self.settings.processing_limits[1], pd.Timestamp):
            end = self.settings.processing_limits[1].isoformat(
                sep=" ", timespec="seconds"
            )
        else:
            end = str(self.settings.processing_limits[1])
        self.end_edit = QLineEdit(end)
        self.end_edit.setToolTip(
            "Can be either a FRAMENUMBER (integer) "
            "or a TIMESTAMP (YYYY-MM-DD HH:MM:SS)"
        )
        self.end_edit.setPlaceholderText("last frame")
        self.end_edit.setMinimumHeight(30)

        # row layout
        limits_row = QHBoxLayout()
        limits_row.addWidget(QLabel("Start:"))
        limits_row.addWidget(self.start_edit)
        limits_row.addWidget(QLabel("End:"))
        limits_row.addWidget(self.end_edit)

        # timestamp format example
        example_label = QLabel(
            "either a FRAMENUMBER or a TIMESTAMP (e.g. YYYY-MM-DD HH:MM:SS)"
        )
        example_label.setStyleSheet(
            "font-size: 12px; color: #666; font-style: italic;"
        )

        limits_infos_row = QHBoxLayout()
        limits_infos_row.addWidget(
            example_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # row layout
        form.addRow("Limits", limits_row)
        form.addRow(limits_infos_row)
        form.addRow(self.Qhline())

        #######################################
        #   SETTINGS BUTTONS   #
        #######################################
        btn_style = get_btn_style(size=13)

        # load settings
        self.load_settings_btn = QPushButton("Load settings")
        self.load_settings_btn.setToolTip("Load settings from a JSON file.")
        self.load_settings_btn.setStyleSheet(btn_style)
        self.load_settings_btn.setFixedWidth(120)
        self.load_settings_btn.clicked.connect(self.on_load_settings)

        # save settings
        self.save_settings_btn = QPushButton("Save settings")
        self.save_settings_btn.setToolTip(
            "Save current settings to a JSON file."
        )
        self.save_settings_btn.setStyleSheet(btn_style)
        self.save_settings_btn.setFixedWidth(120)
        self.save_settings_btn.clicked.connect(self.on_save_settings)

        # set default settings
        self.default_settings_btn = QPushButton("Define as default")
        self.default_settings_btn.setToolTip(
            "Save current settings as default."
        )
        self.default_settings_btn.setStyleSheet(btn_style)
        self.default_settings_btn.setFixedWidth(120)
        self.default_settings_btn.clicked.connect(self.on_default_settings)

        # row layout
        settings_row = QHBoxLayout()
        settings_row.addStretch(1)
        settings_row.addWidget(self.load_settings_btn)
        settings_row.addWidget(self.save_settings_btn)
        settings_row.addWidget(self.default_settings_btn)
        settings_row.addStretch(1)

        form.addRow(settings_row)
        form.addRow(self.Qhline())

        #######################################
        #   VALIDATION BUTTONS   #
        #######################################
        # process
        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        ok_btn = QPushButton("Process")
        ok_btn.setFixedWidth(100)
        ok_btn.setStyleSheet(btn_style)
        ok_btn.clicked.connect(self.on_accept)

        # cancel
        btn_style = get_btn_style(size=15, bold=True)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet(btn_style)
        cancel_btn.clicked.connect(self.on_reject)

        # row layout
        validation_row = QHBoxLayout()
        validation_row.addStretch(1)
        validation_row.addWidget(ok_btn)
        validation_row.addWidget(cancel_btn)
        validation_row.addStretch(1)

        form.addRow(validation_row)

        self.setLayout(form)
        ok_btn.setFocus()
        self._update_ui_from_settings()

    #######################################
    #   UI x Settings   #
    #######################################

    def _update_ui_from_settings(self):
        """Update UI elements based on LMT-EYE settings."""
        settings = self.settings.get_as_str_dict()

        self.start_edit.setText(settings["processing_limits"][0])
        self.end_edit.setText(settings["processing_limits"][1])
        self.output_folder_edit.setText(settings["output_folder"])

        selected_known_events = self.get_selected_known_events()
        custom_events = self.settings.events - selected_known_events
        self.custom_event_edit.setText(", ".join(custom_events))

        self.animal_type_box.setCurrentText(self.settings.animal_type.name)
        self.flickering_cb.setChecked(self.settings.filter_flickering)
        self.stop_cb.setChecked(self.settings.filter_stop)
        self.time_window_frames.setValue(self.settings.time_window)
        self._on_time_frames_changed()  # to update minutes accordingly
        self.process_window_frames.setValue(self.settings.processing_window)
        self._on_process_frames_changed()  # to update hours accordingly
        self.fps_spin.setValue(self.settings.fps)
        self.night_begin_spin.setValue(self.settings.night_begin)
        self.night_duration_spin.setValue(self.settings.night_duration)
        self.rebuild_box.setChecked(self.settings.rebuild_events)
        self.utc_offset_spin.setValue(self.settings.UTC_offset)

    def _update_settings_from_ui(self):
        """Update LMT-EYE settings based on current UI values."""
        self.settings.output_folder = (
            Path(self.output_folder_edit.text())
            if self.output_folder_edit.text()
            else None
        )
        self.settings.animal_type = AnimalType[
            self.animal_type_box.currentText()
        ]
        self.settings.filter_flickering = self.flickering_cb.isChecked()
        self.settings.filter_stop = self.stop_cb.isChecked()
        self.settings.time_window = self.time_window_frames.value()
        self.settings.processing_window = self.process_window_frames.value()
        self.settings.fps = self.fps_spin.value()
        self.settings.night_begin = self.night_begin_spin.value()
        self.settings.night_duration = self.night_duration_spin.value()
        self.settings.rebuild_events = self.rebuild_box.isChecked()
        self.settings.UTC_offset = self.utc_offset_spin.value()
        self._update_custom_events()

        start_text = self.start_edit.text().strip()
        if not start_text:
            start = None
        elif start_text.isdigit():
            start = int(start_text)
        else:
            try:
                start = pd.Timestamp(start_text)
            except:
                print("Invalid timestamp format. Setting start to None.")
                start = None

        end_text = self.end_edit.text()
        if not end_text:
            end = None
        elif end_text.isdigit():
            end = int(end_text)
        else:
            try:
                end = pd.Timestamp(end_text)
            except:
                print("Invalid timestamp format. Setting end to None.")
                end = None

        limits = (start, end)

        self.settings.processing_limits = limits

    #######################################
    #   UPDATE FUNCTIONS   #
    #######################################

    def _clamp_time_window_values(self, frames: int):
        """Clamp time window frames and update minutes accordingly."""
        fpm = self.fps_spin.value() * 60  # frames per minute
        minutes = frames / fpm

        min_frames = 1  # 1 frame
        max_frames = 7 * 24 * 60 * fpm  # 7 days

        if frames < min_frames:
            frames = min_frames
            minutes = frames / fpm

        if frames > max_frames:
            frames = max_frames
            minutes = frames / fpm

        self.time_window_frames.setValue(frames)
        self.time_window_minutes.setValue(minutes)

    def _on_time_frames_changed(self):
        """Handle changes in time window frames spinbox."""
        self.time_window_frames.blockSignals(True)
        self.time_window_minutes.blockSignals(True)

        frames = self.time_window_frames.value()
        self._clamp_time_window_values(frames)

        self.time_window_frames.blockSignals(False)
        self.time_window_minutes.blockSignals(False)

    def _on_time_minutes_changed(self):
        """Handle changes in time window minutes spinbox."""
        self.time_window_frames.blockSignals(True)
        self.time_window_minutes.blockSignals(True)

        fpm = self.fps_spin.value() * 60  # frames per minute
        minutes = self.time_window_minutes.value()
        frames = int(minutes * fpm)
        self._clamp_time_window_values(frames)

        self.time_window_frames.blockSignals(False)
        self.time_window_minutes.blockSignals(False)

    def _clamp_process_window_values(self, frames: int):
        """Clamp processing window frames and update minutes accordingly."""
        fph = self.fps_spin.value() * 60 * 60  # frames per hour
        hours = frames / fph

        min_frames = fph  # 1 hour
        max_frames = 7 * 24 * fph  # 7 days

        if frames < min_frames:
            frames = min_frames
            hours = frames / fph

        if frames > max_frames:
            frames = max_frames
            hours = frames / fph

        self.process_window_frames.setValue(frames)
        self.process_window_hours.setValue(hours)

    def _on_process_frames_changed(self):
        self.process_window_frames.blockSignals(True)
        self.process_window_hours.blockSignals(True)

        frames = self.process_window_frames.value()
        self._clamp_process_window_values(frames)

        self.process_window_frames.blockSignals(False)
        self.process_window_hours.blockSignals(False)

    def _on_process_hours_changed(self):
        self.process_window_frames.blockSignals(True)
        self.process_window_hours.blockSignals(True)

        fph = self.fps_spin.value() * 60 * 60  # frames per hour
        hours = self.process_window_hours.value()
        frames = int(round(hours * fph))
        self._clamp_process_window_values(frames)

        self.process_window_frames.setValue(frames)
        self.process_window_frames.blockSignals(False)
        self.process_window_hours.blockSignals(False)

    def _on_fps_changed(self):
        # When FPS changes, update both minutes <-> frames for both windows
        self._on_time_frames_changed()
        self._on_process_frames_changed()

    def _evaluate_night_end(self):
        begin = self.night_begin_spin.value()
        duration = self.night_duration_spin.value()
        end = (begin + duration) % 24
        self.night_end_label.setText(f"End: {end} h")

    def _update_custom_events(self):
        """Update settings.events from the UI by keeping only known events and
        current custom events."""
        selected_known_events = self.get_selected_known_events()
        custom_events = self.get_custom_events_from_ui()
        self.settings.events = selected_known_events | custom_events

    #######################################
    #   UTILS FUNCTIONS   #
    #######################################

    def get_custom_events_from_ui(self):
        """Get the custom events from UI as a set."""
        custom_list = self.custom_event_edit.text().split(",")
        custom_set = {event.strip() for event in custom_list if event.strip()}
        return custom_set

    def get_selected_known_events(self):
        """Get all events present in both settings.events and ALL_EVENTS.
        It corresponds to the events that are selected in the UI (through
        EventSelectionDialog) and are known by the app (i.e. for which the
        app has a specific analysis implemented).
        """
        known_events = set(ALL_EVENTS.keys())
        selected_events = self.settings.events & known_events
        return selected_events

    def on_select_events(self):
        dlg = EventSelectionDialog(self, self.settings.events)
        if dlg.exec():
            self.settings.events = dlg.selected_events
            self._update_custom_events()

    def select_output_folder(self):
        """Open a dialog to choose output folder."""
        folder_str = QFileDialog.getExistingDirectory(
            self, "Select Output Folder"
        )
        if folder_str:
            self.output_folder_edit.setText(folder_str)
        else:
            self.output_folder_edit.setText(None)

    def on_save_settings(self):
        """Save current settings from UI to a JSON file."""
        save_str, _ = QFileDialog.getSaveFileName(
            self,
            "Select Settings File",
            str(SettingsWindow.SAVING_PATH),
            "JSON Files (*.json)",
        )
        save_path = Path(save_str) if save_str else None
        if save_path is None:
            print("No file selected.")
            return
        self._update_settings_from_ui()
        self.settings.save(save_path)

    def on_load_settings(self):
        """Load settings from a JSON file and update UI."""
        load_str, _ = QFileDialog.getOpenFileName(
            self,
            "Select Settings File",
            str(SettingsWindow.SAVING_PATH),
            "JSON Files (*.json)",
        )
        load_path = Path(load_str) if load_str else None
        if load_path is None:
            print("No file selected.")
            return
        self.settings.load(load_path)
        self._update_ui_from_settings()

    def on_default_settings(self):
        """Save current settings as the default settings
        (default_settings.json in the same directory)."""
        save_path = SettingsWindow.SAVING_PATH / "default_settings.json"
        self._update_settings_from_ui()
        self.settings.save(save_path)

    def on_accept(self):
        """Collect settings and accept dialog."""
        self._update_settings_from_ui()
        self.accept()

    def on_reject(self):
        """Clear selected settings and reject dialog."""
        self._update_settings_from_ui()
        self.reject()

    def Qhline(self):
        """Utility function to create a horizontal line separator."""
        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setFrameShadow(QFrame.Shadow.Sunken)
        hline.setFixedHeight(1)
        return hline


class EventSelectionDialog(QDialog):
    """PyQt6 Dialog to select which analysis to perform"""

    def __init__(
        self,
        parent: QWidget | None,
        preselected_events: set[str] | None = None,
    ):
        super().__init__(parent)
        if preselected_events is None:
            preselected_events = set()
        self.selected_events: set[str] = preselected_events
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Select all wanted events")
        self.setFixedSize(1000, 400)
        layout = QVBoxLayout()

        label = QLabel("Available events:")
        label.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(
            label,
            alignment=Qt.AlignmentFlag.AlignHCenter
            | Qt.AlignmentFlag.AlignTop,
        )

        grid_layout = QGridLayout()
        self.analysis_options = []
        max_col = 4
        max_row = (len(ALL_EVENTS) + max_col - 1) // max_col
        row = 0
        col = 0
        for text in list(ALL_EVENTS.keys()):
            cb = QCheckBox(text)
            grid_layout.addWidget(cb, row, col)
            self.analysis_options.append(cb)
            if text in self.selected_events:
                cb.setChecked(True)
            row += 1
            if row >= max_row:
                col += 1
                row = 0

        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(grid_widget)
        layout.addWidget(scroll_area)

        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        self.proceed_btn = QPushButton("Validate Selection")
        self.proceed_btn.setStyleSheet(btn_style)
        self.proceed_btn.clicked.connect(self.on_validation)
        layout.addWidget(
            self.proceed_btn, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.setLayout(layout)

    def on_validation(self):
        """Get all selected events."""
        self.selected_events = self.get_selected_events()
        if self.selected_events:
            list_events = ", ".join(self.selected_events)
        else:
            list_events = "No event selected"
        print(f"Selected events: {list_events}.")
        self.accept()

    def get_selected_events(self) -> set[str]:
        """Return a set of event names for checked checkboxes."""
        return {cb.text() for cb in self.analysis_options if cb.isChecked()}


class UpdateDatabaseInfo(QDialog):
    """Dialog to update animals information in the database."""

    AVAILABLE_COLUMNS = {
        "ID",
        "RFID",
        "GENOTYPE",
        "NAME",
        "AGE",
        "SEX",
        "STRAIN",
        "SETUP",
        "IND",
    }

    @staticmethod
    def smart_cast(s: str):
        """Try to convert a string to int or float if possible, otherwise
        return the original string."""
        s = s.strip()
        try:
            value = int(s)
        except ValueError:
            try:
                value = float(s)
            except ValueError:
                value = s
        return value

    def __init__(self, parent: QWidget | None, database_path: Path):
        """Initialize the dialog and load database information."""
        super().__init__(parent)
        self.setWindowTitle("LMT-EYE - Animals Table")

        self.database_path = database_path
        self.df = self.get_db_df()
        self._init_ui()

    def _init_ui(self):

        #######################################
        #   Columns buttons   #
        #######################################
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        btn_style = get_btn_style()

        self.validate_btn = QPushButton("Validate")
        self.validate_btn.setStyleSheet(btn_style)
        self.validate_btn.clicked.connect(self.on_validate)
        btn_layout.addWidget(self.validate_btn)

        self.add_col_btn = QPushButton("Add Column")
        self.add_col_btn.setStyleSheet(btn_style)
        self.add_col_btn.clicked.connect(self.on_add_column)
        btn_layout.addWidget(self.add_col_btn)

        self.del_col_btn = QPushButton("Delete Column")
        self.del_col_btn.setStyleSheet(btn_style)
        self.del_col_btn.clicked.connect(self.on_delete_column)
        btn_layout.addWidget(self.del_col_btn)

        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

        #######################################
        #   Table   #
        #######################################
        self.table = QTableWidget()
        self.table.setMinimumSize(800, 400)
        self.table.cellChanged.connect(self.on_cell_changed)
        self.build_table_from_df()

        layout.addWidget(self.table)
        self.setLayout(layout)

    def build_table_from_df(self):
        self.table.blockSignals(True)
        self.table.clear()
        self.table.setRowCount(len(self.df))
        self.table.setColumnCount(len(self.df.columns))
        self.table.setHorizontalHeaderLabels(self.df.columns)

        protected = {"ID", "RFID"}

        for row_idx, (_, row) in enumerate(self.df.iterrows()):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_idx, j, item)
                col_name = self.df.columns[j]
                if col_name in protected:
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

    def on_cell_changed(self, row: int, column: int):
        protected = {"GENOTYPE", "NAME"}
        item = self.table.item(row, column)
        if item is None:
            return

        col_name = self.df.columns[column]
        col_type = self.df[col_name].dtype

        if col_name in protected:
            new_value = item.text()
        else:
            new_value = UpdateDatabaseInfo.smart_cast(item.text())

        correct_value = None

        if col_type == type(new_value):
            correct_value = new_value

        if col_type.kind == "O":  # object, usually string
            if type(new_value) != str:
                correct_value = str(new_value)
            else:
                correct_value = new_value

        if col_type.kind == "f":
            if type(new_value) == int:
                correct_value = float(new_value)
            if type(new_value) == str and new_value == "":
                correct_value = np.nan
                item.setText("nan")

        if col_type.kind == "i":
            if type(new_value) == float and new_value.is_integer():
                correct_value = int(new_value)
            if type(new_value) == str and new_value == "":
                correct_value = 0
                item.setText("0")

        if correct_value is None:
            self.table.blockSignals(True)
            expected_type = "UNKNOWN"
            if col_type.kind == "f":
                expected_type = "REAL (float)"
            if col_type.kind == "i":
                expected_type = "INTEGER (int)"
            if col_type.kind == "O":
                expected_type = "TEXT (str)"
            warning_msg = (
                f"Column '{col_name}' expects a {expected_type}. "
                "Reverting to previous value."
            )
            QMessageBox.warning(
                self,
                "Invalid Input",
                warning_msg,
            )
            old_value = self.df.at[row, col_name]
            item.setText(str(old_value))
            self.table.blockSignals(False)
        else:
            self.df.at[row, col_name] = correct_value

    def on_add_column(self):
        #######################################
        #   Choose any column name   #
        #######################################
        # col_name, ok = QInputDialog.getText(self, "Add Column", "Column name:")
        # col_name = col_name.strip().upper()
        # if not ok:
        #     return
        # if not col_name:
        #     QMessageBox.information(self, "Cancel", f"Invalid column name.")
        #     return
        # for col in self.df.columns:
        #     if col_name == col:
        #         QMessageBox.information(
        #             self, "Cancel", f"Column '{col_name}' already exists."
        #         )
        #         return

        #######################################
        #   Choose column name from list   #
        #######################################
        available = list(self.AVAILABLE_COLUMNS - set(self.df.columns))
        if not available:
            QMessageBox.information(
                self,
                "No Available Columns",
                "All available columns have already been added.",
            )
            return
        col_name, ok = QInputDialog.getItem(
            self,
            "Add Column",
            "Select column to add:",
            available,
            editable=False,
        )
        if not ok or not col_name:
            return

        dlg = SQLTypeDialog(self)
        if not dlg.exec():
            return

        col_type = dlg.get_choosen_type()
        if col_type == "TEXT":
            default = ""
        elif col_type == "REAL":
            default = np.nan
        elif col_type == "INTEGER":
            default = 0
        else:
            default = None
        self.df[col_name] = pd.Series([default] * len(self.df))
        self.build_table_from_df()

    def on_delete_column(self):
        protected = {"ID", "RFID", "GENOTYPE", "NAME"}
        cols = [col for col in self.df.columns if col not in protected]
        if not cols:
            QMessageBox.information(
                self,
                "No Deletable Columns",
                "No columns available for deletion.",
            )
            return
        col_name, ok = QInputDialog.getItem(
            self, "Delete Column", "Select column to delete:", cols, 0, False
        )
        if not ok or not col_name:
            return
        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            (
                f"Are you sure you want to delete column '{col_name}'? "
                "This cannot be undone."
            ),
        )
        if not confirm:
            return
        self.df.drop(columns=[col_name], inplace=True)
        self.build_table_from_df()

    def get_db_df(self):
        connection = sqlite3.connect(self.database_path)
        c = connection.cursor()
        c.execute("SELECT * FROM ANIMAL")
        data = c.fetchall()
        columns = [description[0] for description in c.description]
        df = pd.DataFrame(data, columns=columns)
        c.close()
        connection.close()
        return df

    def on_validate(self):
        protected = {"ID", "RFID"}
        try:
            connection = sqlite3.connect(self.database_path)
            c = connection.cursor()

            c.execute("PRAGMA table_info(ANIMAL)")
            db_columns = set([row[1] for row in c.fetchall()])
            df_columns = list(self.df.columns)

            #######################################
            #   Remove exceeding columns   #
            #######################################

            exceeding_cols = [
                col
                for col in db_columns
                if col not in df_columns and col not in protected
            ]
            for col in exceeding_cols:
                alter_sql = f"ALTER TABLE ANIMAL DROP COLUMN {col}"
                c.execute(alter_sql)

            #######################################
            #   Add missing columns   #
            #######################################
            missing_cols = [
                col
                for col in df_columns
                if col not in db_columns and col not in protected
            ]
            for col in missing_cols:
                dtype_kind = self.df[col].dtype.kind
                if dtype_kind == "i":
                    sql_type = "INTEGER"
                elif dtype_kind == "f":
                    sql_type = "REAL"
                else:
                    sql_type = "TEXT"
                alter_sql = f"ALTER TABLE ANIMAL ADD COLUMN {col} {sql_type}"
                c.execute(alter_sql)

            #######################################
            #   Update values in all columns   #
            #######################################
            c.execute("PRAGMA table_info(ANIMAL)")
            db_columns = set([row[1] for row in c.fetchall()])
            update_cols = [
                col
                for col in df_columns
                if col in db_columns and col not in protected
            ]
            for _, row in self.df.iterrows():
                match_col = None
                match_val = None
                if "ID" in df_columns and pd.notna(row["ID"]):
                    match_col = "ID"
                    match_val = row["ID"]
                elif "RFID" in df_columns and pd.notna(row["RFID"]):
                    match_col = "RFID"
                    match_val = row["RFID"]
                else:
                    print(f"Skipping row with no valid ID or RFID: {row}")
                    continue

                set_clause = ", ".join([f"{col}=?" for col in update_cols])
                values = [row[col] for col in update_cols]
                values.append(match_val)
                c.execute(
                    f"UPDATE ANIMAL SET {set_clause} WHERE {match_col}=?",
                    values,
                )
            connection.commit()
            c.close()
            connection.close()
            QMessageBox.information(self, "Validated", "Database updated.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to update database: {e}"
            )


class SQLTypeDialog(QDialog):
    """Dialog to select a type for a new column in the database."""

    INFOS = {
        "TEXT": "Any text string.",
        "INTEGER": "Whole numbers (int).",
        "REAL": "Floating point numbers (float).",
    }

    def __init__(self, parent: QWidget | None):
        """Initialize the type selection dialog."""
        super().__init__(parent)
        self.setWindowTitle("Select Column Type")
        layout = QVBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems(self.INFOS.keys())
        layout.addWidget(self.combo)
        self.desc = QLabel()
        layout.addWidget(self.desc)
        self.combo.currentTextChanged.connect(self.update_type_description)
        self.update_type_description(self.combo.currentText())
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def update_type_description(self, t):
        """Update the description label based on the selected type."""
        self.desc.setText(f"<i>{self.INFOS[t]}</i>")

    def get_choosen_type(self):
        """Return the selected SQL type as a string."""
        return self.combo.currentText()


class ProgressDialog(QDialog):
    """A modal progress dialog with a label and progress bar."""

    def __init__(
        self,
        title="Processing...",
        label_text="Please wait...",
        parent=None,
        maximum=0,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(350, 120)
        layout = QVBoxLayout(self)
        self.label = QLabel(label_text)
        self.progress = QProgressBar()
        self.progress.setRange(0, maximum)
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

    def set_label(self, text):
        self.label.setText(text)

    def set_progress(self, value):
        self.progress.setValue(value)

    def set_maximum(self, maximum):
        self.progress.setMaximum(maximum)

    # def closeEvent(self, event):
    #     # Prevent closing if desired (optional)
    #     event.accept()


def exception_hook(type_, value, tb):
    """Global exception hook to catch unhandled exceptions and display them in
    a message box."""
    traceback.print_exception(type_, value, tb)
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Application Error")
    msg.setText("An unexpected error occurred.")
    msg.setDetailedText("".join(traceback.format_exception(type_, value, tb)))
    msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    app.setApplicationVersion(APP_VERSION[0])
    app.setApplicationName("LMT-EYE")

    sys.excepthook = exception_hook

    window = AnalysisAppWindow()

    window.show()
    sys.exit(app.exec())
