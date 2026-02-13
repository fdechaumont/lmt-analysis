"""
@creation: 15-01-2026
@author: xmousset
"""

import sys
import sqlite3
from pathlib import Path
from typing import Any, Literal

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
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

lmt_analysis_path = Path(__file__).parent.parent
sys.path.append(lmt_analysis_path.as_posix())

from dim_c_brains.scripts.pyqt6_tools import (
    UserSelector,
    YesNoQuestion,
    get_btn_style,
)
from dim_c_brains.scripts.events_and_modules import ALL_EVENTS
from dim_c_brains.LMT_analyser import LMTAnalyser, AnalysisSettings
from dim_c_brains.scripts.events_rebuilder import RebuildOption
from dim_c_brains.scripts.parameter_saver import ParameterSaver
from lmtanalysis.Measure import oneMinute, oneDay
from lmtanalysis.Animal import AnimalType


class AnalysisAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LMT Analysis App")
        self.setFixedSize(550, 400)
        self.setWindowIcon(QIcon("LMT/dim_c_brains/res/app_icon.png"))

        self.database_path = None

        self.settings = AnalysisSettings()
        self.load_default_settings()

        self.init_ui()

    def load_default_settings(self):
        """Load default settings if available."""
        default_path = (
            Path(__file__).parent
            / "res"
            / "saved_configs"
            / "default_settings.json"
        )
        if default_path.is_file():
            self.settings.load(default_path)
        else:
            print("Warning: 'default_settings.json' not found.")

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Info display
        self.info_label = QLabel()
        self.info_label.setTextFormat(Qt.TextFormat.RichText)
        self.info_label.setText("<b>No loaded database.</b>")
        main_layout.addWidget(self.info_label)

        #######################################
        #   First buttons row   #
        #######################################
        btn_layout = QHBoxLayout()

        # database button
        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        self.load_db_btn = QPushButton("Load Database")
        self.load_db_btn.setStyleSheet(btn_style)
        self.load_db_btn.clicked.connect(self.on_load_db)
        btn_layout.addWidget(self.load_db_btn)

        # all other buttons
        btn_style = get_btn_style(size=15, bold=True)

        # update animals information button
        self.update_info_btn = QPushButton("Animals Infos")
        self.update_info_btn.setStyleSheet(btn_style)
        self.update_info_btn.clicked.connect(self.on_update_info)
        btn_layout.addWidget(self.update_info_btn)

        # settings button
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setStyleSheet(btn_style)
        self.settings_btn.clicked.connect(self.on_settings)
        btn_layout.addWidget(self.settings_btn)

        main_layout.addLayout(btn_layout)

        #######################################
        #   Second buttons row   #
        #######################################
        btn_layout = QHBoxLayout()

        # Rebuild button
        self.rebuild_btn = QPushButton("Rebuild")
        self.rebuild_btn.setStyleSheet(btn_style)
        self.rebuild_btn.clicked.connect(self.on_rebuild)
        btn_layout.addWidget(self.rebuild_btn)

        # Process and Rebuild button
        self.rebuild_process_btn = QPushButton("Rebuild + Process")
        self.rebuild_process_btn.setStyleSheet(btn_style)
        self.rebuild_process_btn.clicked.connect(self.on_rebuild_analyse)
        btn_layout.addWidget(self.rebuild_process_btn)

        # Process button
        self.process_btn = QPushButton("Process")
        self.process_btn.setStyleSheet(btn_style)
        self.process_btn.clicked.connect(self.on_analyse)
        btn_layout.addWidget(self.process_btn)

        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def update_info(self):
        infos = {}
        if self.database_path is not None:
            t_format = "%Y %B - %A %d - %H:%M"
            infos = LMTAnalyser.get_informations(self.database_path)
            info_html = (
                "<table style='font-size:13px;'>"
                f"<tr><td><b>Database:</b></td><td>{infos["database_name"]}</td></tr>"
                f"<tr><td><b>Animals:</b></td><td>{infos["n_animals"]}</td></tr>"
                f"<tr><td><b>Start:</b></td><td>{infos["start_time"].strftime(t_format)}</td></tr>"
                f"<tr><td><b>End:</b></td><td>{infos["end_time"].strftime(t_format)}</td></tr>"
                f"<tr><td><b>Duration:</b></td><td>{infos["duration"].days} days, {infos["duration"].seconds // 3600} hours and {(infos["duration"].seconds // 60) % 60} minutes</td></tr>"
                f"<tr><td><b>FPS:</b></td><td>{infos["fps"]:.1f}</td></tr>"
                "</table>"
            )
            self.info_label.setText(info_html)
        else:
            info_html = (
                "<table style='font-size:13px;'>"
                "<tr><td><b>Database:</b></td><td>No loaded database.</td></tr>"
                "</table>"
            )

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
        self.update_info()

        btn_style = get_btn_style(size=15, bold=True)
        self.load_db_btn.setStyleSheet(btn_style)

        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")
        self.rebuild_btn.setStyleSheet(btn_style)
        self.rebuild_process_btn.setStyleSheet(btn_style)
        self.process_btn.setStyleSheet(btn_style)

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

    def on_settings(self):
        """Launches a dialog/class for rebuild options."""
        dlg = SettingsWindow(self, self.settings)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.settings.update_from_dict(dlg.selected_settings)

    def on_rebuild(self):
        """Rebuild database without processing."""
        if self.database_path is None:
            self.warning_message_load_database()
            return

        msg = f"Rebuild {self.database_path.stem} ?"
        dlg = YesNoQuestion(self, msg)

        if dlg.exec():
            print("Rebuilding database...")
            current_settings = self.settings.get_as_dict()
            current_settings["database_path"] = self.database_path
            self.lmt_analyser = LMTAnalyser(**current_settings)
            self.lmt_analyser.rebuild_database()
            print("Rebuild finished.")
        else:
            print("Process cancelled.")

    def on_rebuild_analyse(self):
        """Rebuild database then analyse it."""
        if self.database_path is None:
            self.warning_message_load_database()
            return

        msg = f"Rebuild and analyse {self.database_path.stem} ?"
        dlg = YesNoQuestion(self, msg)

        if dlg.exec():
            current_settings = self.settings.get_as_dict()
            current_settings["database_path"] = self.database_path
            self.lmt_analyser = LMTAnalyser(**current_settings)
            print("Rebuilding database...")
            self.lmt_analyser.rebuild_database()
            print("Rebuild finished.")
            print("Starting analysis...")
            self.lmt_analyser.run_analysis()
            print("Analysis finished.")
        else:
            print("Process cancelled.")

    def on_analyse(self):
        """Analyse database without rebuild."""
        if self.database_path is None:
            self.warning_message_load_database()
            return

        msg = f"Analyse {self.database_path.stem} ?"
        dlg = YesNoQuestion(self, msg)

        if dlg.exec():
            current_settings = self.settings.get_as_dict()
            current_settings["database_path"] = self.database_path
            self.lmt_analyser = LMTAnalyser(**current_settings)
            print("Starting analysis...")
            self.lmt_analyser.run_analysis()
            print("Analysis finished.")
        else:
            print("Process cancelled.")


class EventChooser(QDialog):
    """PyQt6 Dialog to select which analysis to perform"""

    def __init__(
        self,
        preselected_events: list[str] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.selected_events: list[str] = []
        if preselected_events is not None:
            self.selected_events = preselected_events
        self._init_ui()

    def on_validation(self):
        """Handles validation of selected events."""
        self.selected_events = self.get_selected_events()
        if self.selected_events:
            list_events = ", ".join(self.selected_events)
        else:
            list_events = "No event selected"
        print(f"Selected events: {list_events}.")
        self.accept()

    def get_selected_events(self) -> list[str]:
        """Return a list of event names for checked checkboxes."""
        return [cb.text() for cb in self.analysis_options if cb.isChecked()]

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

        self.proceed_btn = QPushButton("Validate Selection")
        self.proceed_btn.setStyleSheet(
            "font-size: 15px; font-weight: bold; background-color: #1976D2; "
            "color: white; border-radius: 6px; padding: 8px 0;"
        )
        self.proceed_btn.clicked.connect(self.on_validation)
        layout.addWidget(
            self.proceed_btn, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.setLayout(layout)


class SettingsWindow(QDialog):
    """Dialog to edit LMTAnalyser settings."""

    def __init__(self, parent: QWidget, settings: AnalysisSettings):
        """Initialize the settings window with current settings."""
        super().__init__(parent)
        self.setWindowTitle("Select LMT Analysis Settings")
        # self.setFixedSize(700, 600)
        self.selected_settings = settings.get_as_dict()
        self._init_ui()

    def _init_ui(self):

        layout = QVBoxLayout()
        form = QFormLayout()

        #######################################
        #   Output folder   #
        #######################################
        if self.selected_settings["output_folder"] is None:
            self.output_folder_edit = QLineEdit()
        else:
            self.output_folder_edit = QLineEdit(
                str(self.selected_settings["output_folder"])
            )
        out_btn = QPushButton("Browse")
        btn_style = get_btn_style()
        out_btn.setStyleSheet(btn_style)
        out_btn.setFixedWidth(80)

        out_btn.clicked.connect(self.choose_output_folder)
        out_row = QHBoxLayout()
        out_row.addWidget(self.output_folder_edit)
        out_row.addWidget(out_btn)
        form.addRow("Output Folder:", out_row)

        #######################################
        #   Animal Type   #
        #######################################
        self.animal_type_box = QComboBox()
        options = [animal_type.name for animal_type in AnimalType]
        self.animal_type_box.addItems(options)
        current_type = str(self.selected_settings["animal_type"])
        if current_type in options:
            self.animal_type_box.setCurrentText(current_type)
        animal_type_row = QHBoxLayout()
        animal_type_label = QLabel("Animal Type:")
        animal_type_row.addWidget(animal_type_label)
        animal_type_row.addSpacing(10)
        animal_type_row.addWidget(self.animal_type_box)
        animal_type_row.addStretch(1)
        animal_type_widget = QWidget()
        animal_type_widget.setLayout(animal_type_row)
        form.addRow(animal_type_widget)

        form.addRow(self.Qhline())
        #######################################
        #   ANALYSIS FILTERS   #
        #######################################
        filter_row = QHBoxLayout()

        # Flickering
        self.flickering_cb = QCheckBox()
        self.flickering_cb.setChecked(
            self.selected_settings["filter_flickering"]
        )
        filter_row.addWidget(QLabel("Flickering:"))
        filter_row.addWidget(self.flickering_cb)

        filter_row.addSpacing(20)

        # Stop
        self.stop_cb = QCheckBox()
        self.stop_cb.setChecked(self.selected_settings["filter_stop"])
        filter_row.addWidget(QLabel("Stop:"))
        filter_row.addWidget(self.stop_cb)

        filter_widget = QWidget()
        filter_widget.setLayout(filter_row)
        form.addRow("Filters:", filter_widget)

        form.addRow(self.Qhline())
        #######################################
        #   TIME, PROCESSING and FPS   #
        #######################################

        # time_window (frames and minutes)
        self.time_window_frames = QSpinBox()
        self.time_window_frames.setRange(1, 100_000_000)
        self.time_window_frames.setValue(self.selected_settings["time_window"])

        self.time_window_minutes = QDoubleSpinBox()
        self.time_window_minutes.setDecimals(0)
        self.time_window_minutes.setRange(0, 100_000)
        self.time_window_minutes.setValue(
            int(
                self.selected_settings["time_window"]
                / (self.selected_settings["fps"] * 60)
            )
        )
        self.time_window_minutes_label = QLabel("min")

        # processing_window (frames and minutes)
        self.process_window_frames = QSpinBox()
        self.process_window_frames.setRange(1, 100_000_000)
        self.process_window_frames.setValue(
            self.selected_settings["processing_window"]
        )

        self.process_window_hours = QDoubleSpinBox()
        self.process_window_hours.setDecimals(0)
        self.process_window_hours.setRange(0, 10_000)
        self.process_window_hours.setValue(
            int(
                self.selected_settings["processing_window"]
                / (self.selected_settings["fps"] * 60 * 60)
            )
        )
        self.process_window_hours_label = QLabel("hours")

        # fps
        self.fps_spin = QSpinBox()
        self.fps_spin.setValue(self.selected_settings["fps"])
        self.fps_spin.setFixedWidth(70)
        fps_row = QHBoxLayout()
        fps_label = QLabel("FPS (frames per second):")
        fps_row.addWidget(fps_label)
        fps_row.addSpacing(10)
        fps_row.addWidget(self.fps_spin)
        fps_row.addStretch(1)

        # sync logic for time, processing and fps
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
        time_row.addWidget(QLabel("Frames:"))
        time_row.addWidget(self.time_window_frames)
        time_row.addSpacing(10)
        time_row.addWidget(QLabel("Minutes:"))
        time_row.addWidget(self.time_window_minutes)
        time_row.addWidget(self.time_window_minutes_label)
        form.addRow("Time Window:", time_row)

        proc_row = QHBoxLayout()
        proc_row.addWidget(QLabel("Frames:"))
        proc_row.addWidget(self.process_window_frames)
        proc_row.addSpacing(10)
        proc_row.addWidget(QLabel("Hours:"))
        proc_row.addWidget(self.process_window_hours)
        proc_row.addWidget(self.process_window_hours_label)
        form.addRow("Processing Window:", proc_row)

        form.addRow(fps_row)

        form.addRow(self.Qhline())
        #######################################
        #   NIGHT TIME   #
        #######################################
        night_row = QHBoxLayout()

        # night begin
        self.night_begin_spin = QSpinBox()
        self.night_begin_spin.setRange(0, 23)
        self.night_begin_spin.setValue(self.selected_settings["night_begin"])
        night_row.addWidget(QLabel("Begin (h):"))
        night_row.addWidget(self.night_begin_spin)

        night_row.addSpacing(20)

        # night duration
        self.night_duration_spin = QSpinBox()
        self.night_duration_spin.setRange(1, 24)
        self.night_duration_spin.setValue(
            self.selected_settings["night_duration"]
        )
        night_row.addWidget(QLabel("Duration (h):"))
        night_row.addWidget(self.night_duration_spin)

        night_row.addSpacing(20)

        # night end (calculated)
        self.night_end_label = QLabel()
        night_row.addWidget(self.night_end_label)

        # connect signals to update night end
        self.night_begin_spin.valueChanged.connect(self._update_night_end)
        self.night_duration_spin.valueChanged.connect(self._update_night_end)
        self._update_night_end()

        night_widget = QWidget()
        night_widget.setLayout(night_row)
        form.addRow("Night Settings:", night_widget)

        form.addRow(self.Qhline())
        #######################################
        #   ANALYSIS LIMITS (start, end)   #
        #######################################
        lim_row = QHBoxLayout()

        # start
        if self.selected_settings["analysis_limits"][0] is None:
            self.start_edit = QLineEdit()
        else:
            self.start_edit = QLineEdit(
                str(self.selected_settings["analysis_limits"][0])
            )
        self.start_edit.setMinimumHeight(30)
        lim_row.addWidget(QLabel("Start:"))
        lim_row.addWidget(self.start_edit)

        # end
        if self.selected_settings["analysis_limits"][1] is None:
            self.end_edit = QLineEdit()
        else:
            self.end_edit = QLineEdit(
                str(self.selected_settings["analysis_limits"][1])
            )
        self.end_edit.setMinimumHeight(30)
        lim_row.addWidget(QLabel("End:"))
        lim_row.addWidget(self.end_edit)

        lim_widget = QWidget()
        lim_widget.setLayout(lim_row)

        # timestamp example
        lim_col = QVBoxLayout()
        lim_col.addWidget(lim_widget)
        example_label = QLabel("<i>Timestamp example: 2026-01-01 13:30:00</i>")
        example_label.setStyleSheet("font-size: 12px; color: #666;")
        lim_col.addWidget(
            example_label, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        lim_container = QWidget()
        lim_container.setLayout(lim_col)
        form.addRow(
            "Analysis Limits:\n-> framenumber\n-> timestamp",
            lim_container,
        )

        # End of form section
        layout.addLayout(form)

        # Add separator before events section
        layout.addWidget(self.Qhline())
        #######################################
        #   EVENTS BUTTONS   #
        #######################################
        self.events_to_analyse: list[str] = self.selected_settings.get(
            "events_to_analyse", []
        )
        self.events_to_rebuild: list[str] = self.selected_settings.get(
            "events_to_rebuild", []
        )
        self.events_in_overview: list[str] = self.selected_settings.get(
            "events_in_overview", []
        )

        # events title
        events_title = QLabel("EVENTS")
        events_title.setStyleSheet(
            """
            font-size: 16px; font-weight: bold;
            color: #ffffff;
            margin-bottom: 4px;
        """
        )
        layout.addWidget(events_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        # buttons
        btn_event_layout = QHBoxLayout()
        btn_style = get_btn_style(size=15, bold=True, bg_color="#1976D2")

        # events to analyse
        self.events_to_analyse_btn = QPushButton("Analysis")
        self.events_to_analyse_btn.setStyleSheet(btn_style)
        self.events_to_analyse_btn.clicked.connect(self.on_events_to_analyse)
        btn_event_layout.addWidget(self.events_to_analyse_btn)

        # events to rebuild
        self.events_to_rebuild_btn = QPushButton("Rebuild")
        self.events_to_rebuild_btn.setStyleSheet(btn_style)
        self.events_to_rebuild_btn.clicked.connect(self.on_events_to_rebuild)
        btn_event_layout.addWidget(self.events_to_rebuild_btn)

        # events in overview
        self.events_in_overview_btn = QPushButton("Overview")
        self.events_in_overview_btn.setStyleSheet(btn_style)
        self.events_in_overview_btn.clicked.connect(self.on_events_in_overview)
        btn_event_layout.addWidget(self.events_in_overview_btn)

        layout.addLayout(btn_event_layout)

        #######################################
        #   Rebuild option   #
        #######################################

        self.rebuild_box = QComboBox()
        options = [ro.name for ro in RebuildOption]
        self.rebuild_box.addItems(options)
        current_opt = str(self.selected_settings["rebuild_option"])
        if current_opt in options:
            self.rebuild_box.setCurrentText(current_opt)
        layout.addWidget(self.Qhline())
        rebuild_row = QHBoxLayout()
        rebuild_label = QLabel("Rebuild Option:")
        rebuild_row.addWidget(rebuild_label)
        rebuild_row.addSpacing(10)
        rebuild_row.addWidget(self.rebuild_box)
        rebuild_row.addStretch(1)
        rebuild_widget = QWidget()
        rebuild_widget.setLayout(rebuild_row)
        layout.addWidget(rebuild_widget)

        # Add info about each rebuild option
        rebuild_info = QLabel(
            """
            <span style='display:inline-block; width:20px; font-size:12px; color:#666;'>
            <span style=""></span><b>NO_REBUILD</b>: do not rebuild any events.<br>
            <b>ALL</b>: rebuild all events that exist for LMT.<br>
            <b>MISSING</b>: rebuild only missing events in database.<br>
            <b>ANALYSIS</b>: rebuild analysis-related events (those in <code>LMTAnalyser.events_to_analyse</code>).<br>
            <b>CUSTOM</b>: rebuild only events specified (those in <code>LMTAnalyser.events_to_rebuild</code>).
            </span>
            """
        )
        rebuild_info.setTextFormat(Qt.TextFormat.RichText)
        rebuild_info.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(rebuild_info)

        layout.addWidget(self.Qhline())
        #######################################
        #   SETTINGS CONFIGURATION BUTTONS   #
        #######################################
        # events title
        events_title = QLabel("SETTINGS")
        events_title.setStyleSheet(
            """
            font-size: 16px; font-weight: bold;
            color: #ffffff;
            margin-bottom: 4px;
        """
        )
        layout.addWidget(events_title, alignment=Qt.AlignmentFlag.AlignHCenter)

        btn_config_layout = QHBoxLayout()
        btn_style = get_btn_style(size=15, bold=True)

        # load config
        self.load_config_btn = QPushButton("Load Config")
        self.load_config_btn.setStyleSheet(btn_style)
        self.load_config_btn.clicked.connect(self.on_load_config)
        btn_config_layout.addWidget(self.load_config_btn)

        # save config
        self.save_config_btn = QPushButton("Save Config")
        self.save_config_btn.setStyleSheet(btn_style)
        self.save_config_btn.clicked.connect(self.on_save_config)
        btn_config_layout.addWidget(self.save_config_btn)

        # default config
        self.default_config_btn = QPushButton("Define as default")
        self.default_config_btn.setStyleSheet(btn_style)
        self.default_config_btn.clicked.connect(self.on_define_default)
        btn_config_layout.addWidget(self.default_config_btn)

        layout.addLayout(btn_config_layout)

        # Add separator before validation section
        layout.addWidget(self.Qhline())
        #######################################
        #   VALIDATION BUTTONS   #
        #######################################
        btn_row = QHBoxLayout()
        btn_style = get_btn_style(size=15, bold=True, bg_color="#449225")
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(100)
        ok_btn.setStyleSheet(btn_style)
        ok_btn.clicked.connect(self.on_accept)

        btn_style = get_btn_style(size=15, bold=True, bg_color="#D24D19")
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setStyleSheet(btn_style)
        cancel_btn.clicked.connect(self.on_reject)

        btn_row.addStretch(1)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch(1)
        layout.addLayout(btn_row)

        self.setLayout(layout)
        ok_btn.setFocus()

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

    def _update_night_end(self):
        begin = self.night_begin_spin.value()
        duration = self.night_duration_spin.value()
        end = (begin + duration) % 24
        self.night_end_label.setText(f"End: {end} h")

    def on_events_to_analyse(self):
        dlg = EventChooser(
            preselected_events=self.events_to_analyse, parent=self
        )
        if dlg.exec():
            self.events_to_analyse = dlg.selected_events

    def on_events_to_rebuild(self):
        dlg = EventChooser(
            preselected_events=self.events_to_rebuild, parent=self
        )
        if dlg.exec():
            self.events_to_rebuild = dlg.selected_events

    def on_events_in_overview(self):
        dlg = EventChooser(
            preselected_events=self.events_in_overview, parent=self
        )
        if dlg.exec():
            self.events_in_overview = dlg.selected_events

    #######################################
    #   UTILS FUNCTIONS   #
    #######################################

    def choose_output_folder(self):
        """Open a dialog to choose output folder."""
        folder_str = QFileDialog.getExistingDirectory(
            self, "Select Output Folder"
        )
        if folder_str:
            self.output_folder_edit.setText(folder_str)
        else:
            self.output_folder_edit.setText(None)

    def choose_config(
        self, save_path: Path, option: Literal["load", "save"] = "save"
    ):
        file_str = ""

        if option == "load":
            file_str, _ = QFileDialog.getOpenFileName(
                self,
                "Select Config",
                str(save_path),
                "JSON Files (*.json)",
            )

        if option == "save":
            file_str, _ = QFileDialog.getSaveFileName(
                self,
                "Select Config",
                str(save_path),
                "JSON Files (*.json)",
            )

        if file_str:
            return Path(file_str)
        else:
            return None

    def on_save_config(self):
        """Save current settings from UI to a JSON file."""
        save_folder = Path(__file__).parent / "res" / "saved_configs"
        save_path = self.choose_config(save_folder, option="save")
        if save_path:
            save_settings = AnalysisSettings()
            save_settings.update_from_dict(self.get_current_settings())
            save_settings.save(save_path)
        else:
            print("No file selected.")

    def on_load_config(self):
        """Load settings from a JSON file and update UI."""
        save_folder = Path(__file__).parent / "res" / "saved_configs"
        load_path = self.choose_config(save_folder, option="load")
        if load_path:
            load_settings = AnalysisSettings()
            load_settings.load(load_path)
            self.set_current_settings(load_settings.get_as_dict())
        else:
            print("No file selected.")

    def on_define_default(self):
        """Save current settings as the default settings
        (default_settings.json in the same directory)."""
        save_path = (
            Path(__file__).parent
            / "res"
            / "saved_configs"
            / "default_settings.json"
        )
        save_settings = AnalysisSettings()
        save_settings.update_from_dict(self.get_current_settings())
        save_settings.save(save_path)

    def get_current_settings(self) -> dict[str, Any]:
        """Collect all current settings from the UI widgets."""
        limits: list[int | None] = [None, None]
        if self.start_edit.text():
            limits[0] = int(self.start_edit.text())

        if self.end_edit.text():
            limits[1] = int(self.end_edit.text())

        output_folder = None
        if self.output_folder_edit.text():
            current_path = Path(self.output_folder_edit.text())
            output_folder = current_path

        settings = {
            "analysis_limits": limits,
            "animal_type": AnimalType[self.animal_type_box.currentText()],
            "events_in_overview": self.events_in_overview,
            "events_to_analyse": self.events_to_analyse,
            "events_to_rebuild": self.events_to_rebuild,
            "filter_flickering": self.flickering_cb.isChecked(),
            "filter_stop": self.stop_cb.isChecked(),
            "fps": self.fps_spin.value(),
            "night_begin": self.night_begin_spin.value(),
            "night_duration": self.night_duration_spin.value(),
            "output_folder": output_folder,
            "processing_window": self.process_window_frames.value(),
            "rebuild_option": RebuildOption[self.rebuild_box.currentText()],
            "time_window": self.time_window_frames.value(),
        }
        return settings

    def set_current_settings(self, settings: dict[str, Any]):
        """Set UI widgets based on provided settings."""
        if "analysis_limits" in settings:
            limits = settings["analysis_limits"]
            self.start_edit.setText(str(limits[0]) if limits[0] else "")
            self.end_edit.setText(str(limits[1]) if limits[1] else "")
        if "animal_type" in settings:
            self.animal_type_box.setCurrentText(settings["animal_type"].name)
        if "events_in_overview" in settings:
            self.events_in_overview = settings["events_in_overview"]
        if "events_to_analyse" in settings:
            self.events_to_analyse = settings["events_to_analyse"]
        if "events_to_rebuild" in settings:
            self.events_to_rebuild = settings["events_to_rebuild"]
        if "filter_flickering" in settings:
            self.flickering_cb.setChecked(settings["filter_flickering"])
        if "filter_stop" in settings:
            self.stop_cb.setChecked(settings["filter_stop"])
        if "fps" in settings:
            self.fps_spin.setValue(settings["fps"])
        if "night_begin" in settings:
            self.night_begin_spin.setValue(settings["night_begin"])
        if "night_duration" in settings:
            self.night_duration_spin.setValue(settings["night_duration"])
        if "output_folder" in settings:
            if settings["output_folder"] is None:
                output_str = ""
            else:
                output_str = str(settings["output_folder"])
            self.output_folder_edit.setText(output_str)
        if "processing_window" in settings:
            self.process_window_frames.setValue(settings["processing_window"])
        if "rebuild_option" in settings:
            self.rebuild_box.setCurrentText(settings["rebuild_option"].name)
        if "time_window" in settings:
            self.time_window_frames.setValue(settings["time_window"])

    def on_accept(self):
        """Collect settings and accept dialog."""
        self.selected_settings = self.get_current_settings()
        self.accept()

    def on_reject(self):
        """Clear selected settings and reject dialog."""
        self.selected_settings: dict[str, Any] = {}
        self.reject()

    def Qhline(self):
        """Utility function to create a horizontal line separator."""
        hline = QFrame()
        hline.setFrameShape(QFrame.Shape.HLine)
        hline.setFrameShadow(QFrame.Shadow.Sunken)
        hline.setFixedHeight(1)
        return hline


class UpdateDatabaseInfo(QDialog):
    """Dialog to update animals information in the database."""

    @staticmethod
    def smart_cast(s: str):
        """Try to convert a string to int or float if possible, otherwise return
        the original string."""
        s = s.strip()
        try:
            value = int(s)
        except ValueError:
            try:
                value = float(s)
            except ValueError:
                value = s
        return value

    def __init__(self, parent: QWidget, database_path: Path):
        """Initialize the dialog and load database information."""
        super().__init__(parent)
        self.setWindowTitle("Update LMT Database Animals Informations")

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
        col_name, ok = QInputDialog.getText(self, "Add Column", "Column name:")
        col_name = col_name.strip().upper()
        if not ok:
            return
        if not col_name:
            QMessageBox.information(self, "Cancel", f"Invalid column name.")
            return
        for col in self.df.columns:
            if col_name == col:
                QMessageBox.information(
                    self, "Cancel", f"Column '{col_name}' already exists."
                )
                return

        dlg = TypeDialog(self)
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


class TypeDialog(QDialog):
    """Dialog to select a type for a new column in the database."""

    INFOS = {
        "TEXT": "Any text string.",
        "INTEGER": "Whole numbers (int).",
        "REAL": "Floating point numbers (float).",
    }

    def __init__(self, parent: QWidget | None = None):
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
        """Return the numpy dtype or str for the selected type."""
        return self.combo.currentText()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = AnalysisAppWindow()
    window.show()
    # # window.raise_()
    # # window.activateWindow()
    sys.exit(app.exec())
