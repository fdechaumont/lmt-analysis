"""
@creation: 15-01-2026
@author: xmousset
"""

import os
import sys
from pathlib import Path
from typing import Literal

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
    QDialog,
)


class UserSelector(QDialog):
    def __init__(
        self,
        parent: QWidget,
        type: Literal["file", "folder"],
        window_title: str | None = None,
    ):
        super().__init__(parent)
        if window_title is None:
            window_title = f"Select {type.capitalize()}"
        self.init_ui(type, window_title)
        if type == "file":
            self.select_sqlite_file()
        else:
            self.select_folder()

    def select_folder(self):
        folder_str = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_str:
            self.selected_path = Path(folder_str)
            self.selection_label.setText(self.selected_path.name)
        else:
            self.selection_label.setText("<i>No folder selected</i>")

    def select_sqlite_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select SQLite file",
            "",
            "SQLite files (*.sqlite);;All files (*)",
        )
        if file_path:
            self.selected_path = Path(file_path)
            self.selection_label.setText(self.selected_path.name)
        else:
            self.selection_label.setText("<i>No file selected</i>")

    def init_ui(self, type: str, window_title: str):
        self.setWindowTitle(window_title)
        self.setFixedSize(420, 170)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 30, 25)
        main_layout.setSpacing(18)

        # Title label
        title_label = QLabel(f"Select a {type} to continue:")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Selection row
        selection_row = QHBoxLayout()
        selection_row.setSpacing(12)

        selection_icon = QLabel()
        style = self.style()
        assert style is not None

        if type == "file":
            icon = QStyle.StandardPixmap.SP_FileIcon
            label = "<i>No file selected</i>"
        elif type == "folder":
            icon = QStyle.StandardPixmap.SP_DirIcon
            label = "<i>No folder selected</i>"
        else:
            raise ValueError("Invalid selection type, use 'file' or 'folder'")

        selection_pixmap = style.standardIcon(icon).pixmap(28, 28)
        selection_icon.setPixmap(selection_pixmap)
        selection_row.addWidget(selection_icon)

        self.selection_label = QLabel(label)

        self.selection_label.setStyleSheet("font-size: 14px; color: #555;")
        self.selection_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.selection_label.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        self.selection_label.setWordWrap(True)
        selection_row.addWidget(
            self.selection_label, 1, Qt.AlignmentFlag.AlignVCenter
        )

        selection_btn = QPushButton("Browse...")
        selection_btn.setFixedWidth(110)
        selection_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 14px;
                padding: 6px 0;
                border-radius: 5px;
                background-color: #e0e0e0;
                color: #222;
            }
            QPushButton:hover {
                background-color: #ffd740;
                color: #000;
            }
            """
        )
        if type == "file":
            selection_btn.clicked.connect(self.select_sqlite_file)
        else:
            selection_btn.clicked.connect(self.select_folder)
        selection_row.addWidget(selection_btn)

        main_layout.addStretch(1)
        main_layout.addLayout(selection_row)
        main_layout.addStretch(1)

        ok_row = QHBoxLayout()
        ok_row.addStretch(1)
        ok_btn = QPushButton("OK")
        ok_btn.setFixedWidth(90)
        ok_btn.setStyleSheet(
            """
            QPushButton {
                font-size: 15px;
                font-weight: bold;
                background-color: #1976D2;
                color: white;
                border-radius: 6px;
                padding: 8px 0;
            }
            QPushButton:hover {
                background-color: #42a5f5;
                color: #fff;
            }
            """
        )
        ok_btn.clicked.connect(self.accept)
        ok_row.addWidget(ok_btn)
        ok_row.addStretch(1)
        main_layout.addLayout(ok_row)

        self.setLayout(main_layout)


class YesNoQuestion(QDialog):
    def __init__(self, parent: QWidget, question: str):
        super().__init__(parent)
        self.question = question
        self.init_ui()

    def yes_clicked(self):
        self.accept()

    def no_clicked(self):
        self.reject()

    def init_ui(self):
        self.setWindowTitle("Yes/No Question Window")
        self.setFixedSize(400, 180)
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(20)

        label = QLabel(self.question)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)

        # YES button
        yes_btn = QPushButton("Yes")
        yes_btn.clicked.connect(self.yes_clicked)
        yes_btn.setFixedWidth(90)
        yes_btn.setStyleSheet(
            """
            background-color: #4CAF50;
            color: white;
            font-size: 15px;
            font-weight: bold;
            padding: 8px 0;
            border-radius: 6px;
        """
        )

        # NO button
        no_btn = QPushButton("No")
        no_btn.clicked.connect(self.no_clicked)
        no_btn.setFixedWidth(90)
        no_btn.setStyleSheet(
            """
            background-color: #F44336;
            color: white;
            font-size: 15px;
            font-weight: bold;
            padding: 8px 0;
            border-radius: 6px;
        """
        )

        # layout setup
        btn_layout.addStretch(1)
        btn_layout.addWidget(yes_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(no_btn)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)


def get_btn_style(
    size: int | None = None,
    bold: bool = False,
    txt_color: str | None = None,
    bg_color: str | None = None,
    border_color: str | None = None,
    hover_txt_color: str | None = None,
    hover_bg_color: str | None = None,
    hover_border_color: str | None = None,
) -> str:

    # base style
    style = "QPushButton {"

    if size is not None:
        style += f"font-size: {size}px; "

    if bold:
        style += f"font-weight: bold; "

    if bg_color is None:
        bg_color = "#333333"
    style += f"background-color: {bg_color}; "

    if txt_color is None:
        txt_color = "#f0f0f0"
    style += f"color: {txt_color}; "

    if border_color is not None:
        border_color = "#f0f0f0"
        style += f"border: 1px solid {border_color}; "
        style += "border-radius: 6px; "

    style += "margin: 6px 6px; padding: 3px 3px; "
    style += " }"

    # hover
    style += "QPushButton:hover {"

    if hover_bg_color is None:
        hover_bg_color = txt_color
    style += f"background-color: {hover_bg_color}; "

    if hover_txt_color is None:
        hover_txt_color = bg_color
    style += f"color: {hover_txt_color}; "

    if hover_border_color is not None:
        hover_border_color = bg_color
        style += f"border: 1.5px solid {hover_border_color};"
        style += "border-radius: 6px; "

    style += " }"

    # return style
    return style
