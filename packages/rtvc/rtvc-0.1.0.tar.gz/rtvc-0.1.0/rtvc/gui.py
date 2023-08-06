import os
import sys

import pkg_resources
import qdarktheme
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from rtvc.audio import get_devices
from rtvc.config import config, load_config, save_config
from rtvc.i18n import _t, language_map


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumWidth(800)

        version = pkg_resources.get_distribution("rtvc").version
        self.setWindowTitle(_t("title").format(version=version))

        self.main_layout = QVBoxLayout()
        # Stick to the top
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.setup_ui_settings()
        self.setup_device_settings()
        self.setup_audio_settings()
        self.setup_action_buttons()

        self.setLayout(self.main_layout)

    def setup_ui_settings(self):
        # we have language and backend settings in the first row
        row = QHBoxLayout()

        # set up a theme combo box
        row.addWidget(QLabel(_t("theme.name")))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem(_t("theme.auto"), "auto")
        self.theme_combo.addItem(_t("theme.light"), "light")
        self.theme_combo.addItem(_t("theme.dark"), "dark")
        self.theme_combo.setCurrentText(_t(f"theme.{config.theme}"))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(100)
        row.addWidget(self.theme_combo)

        # set up language combo box
        row.addWidget(QLabel(_t("i18n.language")))
        self.language_combo = QComboBox()

        for k, v in language_map.items():
            self.language_combo.addItem(v, k)

        self.language_combo.setCurrentText(language_map[config.locale])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.language_combo.setMinimumWidth(150)
        row.addWidget(self.language_combo)

        # set up backend (url) input, and a test button
        row.addWidget(QLabel(_t("backend.name")))
        self.backend_input = QLineEdit()
        self.backend_input.setText(config.backend)
        row.addWidget(self.backend_input)

        self.test_button = QPushButton(_t("backend.test"))
        self.test_button.clicked.connect(self.test_backend)
        row.addWidget(self.test_button)

        self.main_layout.addLayout(row)

    def setup_device_settings(self):
        # second row: a group box for audio device settings
        row = QGroupBox(_t("audio_device.name"))
        row_layout = QGridLayout()
        row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # fetch devices
        input_devices, output_devices = get_devices()

        # input device
        row_layout.addWidget(QLabel(_t("audio_device.input")), 0, 0)
        self.input_device_combo = QComboBox()
        for device in input_devices:
            self.input_device_combo.addItem(device["name"], device["id"])

        # find the current device from config
        if config.input_device is not None:
            for i in range(self.input_device_combo.count()):
                if self.input_device_combo.itemData(i) == config.input_device:
                    self.input_device_combo.setCurrentIndex(i)
                    break
            else:
                # not found, use default
                self.input_device_combo.setCurrentIndex(0)
                config.input_device = self.input_device_combo.itemData(0)

        self.input_device_combo.setFixedWidth(300)
        row_layout.addWidget(self.input_device_combo, 0, 1)

        # output device
        row_layout.addWidget(QLabel(_t("audio_device.output")), 1, 0)
        self.output_device_combo = QComboBox()
        for device in output_devices:
            self.output_device_combo.addItem(device["name"], device["id"])

        # find the current device from config
        if config.output_device is not None:
            for i in range(self.output_device_combo.count()):
                if self.output_device_combo.itemData(i) == config.output_device:
                    self.output_device_combo.setCurrentIndex(i)
                    break
            else:
                # not found, use default
                self.output_device_combo.setCurrentIndex(0)
                config.output_device = self.output_device_combo.itemData(0)

        self.input_device_combo.setFixedWidth(300)
        row_layout.addWidget(self.output_device_combo, 1, 1)

        row.setLayout(row_layout)

        self.main_layout.addWidget(row)

    def setup_audio_settings(self):
        # third row: a group box for audio settings
        row = QGroupBox(_t("audio.name"))
        row_layout = QGridLayout()

        # db_threshold, pitch_shift
        row_layout.addWidget(QLabel(_t("audio.db_threshold")), 0, 0)
        self.db_threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.db_threshold_slider.setMinimum(-60)
        self.db_threshold_slider.setMaximum(0)
        self.db_threshold_slider.setSingleStep(1)
        self.db_threshold_slider.setTickInterval(1)
        self.db_threshold_slider.setValue(config.db_threshold)
        row_layout.addWidget(self.db_threshold_slider, 0, 1)
        self.db_threshold_label = QLabel(f"{config.db_threshold} dB")
        self.db_threshold_label.setFixedWidth(50)
        row_layout.addWidget(self.db_threshold_label, 0, 2)
        self.db_threshold_slider.valueChanged.connect(
            lambda v: self.db_threshold_label.setText(f"{v} dB")
        )

        row_layout.addWidget(QLabel(_t("audio.pitch_shift")), 0, 3)
        self.pitch_shift_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_shift_slider.setMinimum(-24)
        self.pitch_shift_slider.setMaximum(24)
        self.pitch_shift_slider.setSingleStep(1)
        self.pitch_shift_slider.setTickInterval(1)
        self.pitch_shift_slider.setValue(config.pitch_shift)
        row_layout.addWidget(self.pitch_shift_slider, 0, 4)
        self.pitch_shift_label = QLabel(f"{config.pitch_shift}")
        self.pitch_shift_label.setFixedWidth(50)
        row_layout.addWidget(self.pitch_shift_label, 0, 5)
        self.pitch_shift_slider.valueChanged.connect(
            lambda v: self.pitch_shift_label.setText(f"{v}")
        )

        # performance related
        # sample_duration, fade_duration
        row_layout.addWidget(QLabel(_t("audio.sample_duration")), 1, 0)
        self.sample_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.sample_duration_slider.setMinimum(1000)
        self.sample_duration_slider.setMaximum(3000)
        self.sample_duration_slider.setSingleStep(100)
        self.sample_duration_slider.setTickInterval(100)
        self.sample_duration_slider.setValue(config.sample_duration)
        row_layout.addWidget(self.sample_duration_slider, 1, 1)
        self.sample_duration_label = QLabel(f"{config.sample_duration / 1000:.1f} s")
        self.sample_duration_label.setFixedWidth(50)
        row_layout.addWidget(self.sample_duration_label, 1, 2)
        self.sample_duration_slider.valueChanged.connect(
            lambda v: self.sample_duration_label.setText(f"{v / 1000:.1f} s")
        )

        row_layout.addWidget(QLabel(_t("audio.fade_duration")), 1, 3)
        self.fade_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.fade_duration_slider.setMinimum(10)
        self.fade_duration_slider.setMaximum(150)
        self.fade_duration_slider.setSingleStep(10)
        self.fade_duration_slider.setTickInterval(10)
        self.fade_duration_slider.setValue(config.fade_duration)
        row_layout.addWidget(self.fade_duration_slider, 1, 4)
        self.fade_duration_label = QLabel(f"{config.fade_duration / 1000:.2f} s")
        self.fade_duration_label.setFixedWidth(50)
        row_layout.addWidget(self.fade_duration_label, 1, 5)
        self.fade_duration_slider.valueChanged.connect(
            lambda v: self.fade_duration_label.setText(f"{v / 1000:.2f} s")
        )

        # Extra duration, input denoise, output denoise in next row
        row_layout.addWidget(QLabel(_t("audio.extra_duration")), 2, 0)
        self.extra_duration_slider = QSlider(Qt.Orientation.Horizontal)
        self.extra_duration_slider.setMinimum(50)
        self.extra_duration_slider.setMaximum(1000)
        self.extra_duration_slider.setSingleStep(10)
        self.extra_duration_slider.setTickInterval(10)
        self.extra_duration_slider.setValue(config.extra_duration)
        row_layout.addWidget(self.extra_duration_slider, 2, 1)
        self.extra_duration_label = QLabel(f"{config.extra_duration / 1000:.2f} s")
        self.extra_duration_label.setFixedWidth(50)
        row_layout.addWidget(self.extra_duration_label, 2, 2)
        self.extra_duration_slider.valueChanged.connect(
            lambda v: self.extra_duration_label.setText(f"{v / 1000:.2f} s")
        )

        self.input_denoise_checkbox = QCheckBox()
        self.input_denoise_checkbox.setText(_t("audio.input_denoise"))
        self.input_denoise_checkbox.setChecked(config.input_denoise)
        row_layout.addWidget(self.input_denoise_checkbox, 2, 3)

        self.output_denoise_checkbox = QCheckBox()
        self.output_denoise_checkbox.setText(_t("audio.output_denoise"))
        self.output_denoise_checkbox.setChecked(config.output_denoise)
        row_layout.addWidget(self.output_denoise_checkbox, 2, 4)

        row.setLayout(row_layout)
        self.main_layout.addWidget(row)

    def setup_action_buttons(self):
        row = QWidget()
        row_layout = QHBoxLayout()
        # row_layout.setAlignment(Qt.AlignmentFlag.Alig)
        # stick to bottom
        row_layout.addStretch(1)

        self.start_button = QPushButton(_t("action.start"))
        # self.start_button.clicked.connect(self.start_recording)
        row_layout.addWidget(self.start_button)

        self.stop_button = QPushButton(_t("action.stop"))
        self.stop_button.setEnabled(False)
        # self.stop_button.clicked.connect(self.stop_recording)
        row_layout.addWidget(self.stop_button)

        self.latency_label = QLabel(_t("action.latency").format(latency=0))
        row_layout.addWidget(self.latency_label)

        row.setLayout(row_layout)
        self.main_layout.addWidget(row)

    def change_theme(self, index):
        config.theme = self.theme_combo.itemData(index)

        save_config()
        qdarktheme.setup_theme(config.theme)

    def change_language(self, index):
        config.locale = self.language_combo.itemData(index)
        save_config()

        # pop up a message box to tell user app will restart
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setText(_t("i18n.restart_msg"))
        msg_box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        ret = msg_box.exec()

        if ret == QMessageBox.StandardButton.Yes:
            os.execv(sys.argv[0], sys.argv)

    def test_backend(self):
        pass
