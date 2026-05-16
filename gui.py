import asyncio
from PyQt5 import QtCore, QtGui, QtWidgets
from battle_manager import BattleManager
from config import DEFAULT_STOP_HP, DEFAULT_STIM_ENERGY


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Madness RPG Desktop Client")
        self.resize(1200, 760)
        self.manager = BattleManager()
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.setStyleSheet("background-color: #1e1e28; color: #e6e6e6;")
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)

        left_panel = QtWidgets.QFrame()
        left_panel.setMinimumWidth(320)
        left_layout = QtWidgets.QVBoxLayout(left_panel)
        left_layout.setSpacing(14)

        self.hp_bar = QtWidgets.QProgressBar()
        self.hp_bar.setTextVisible(True)
        self.hp_bar.setMaximum(100)
        self.hp_bar.setFormat("HP: 0 / 0")
        self.hp_bar.setStyleSheet("QProgressBar {border: 1px solid #444; border-radius: 8px; background: #2b2b3a;} QProgressBar::chunk {background: #d9534f;}")
        left_layout.addWidget(self.hp_bar)

        self.energy_bar = QtWidgets.QProgressBar()
        self.energy_bar.setTextVisible(True)
        self.energy_bar.setMaximum(100)
        self.energy_bar.setFormat("Energy: 0 / 0")
        self.energy_bar.setStyleSheet("QProgressBar {border: 1px solid #444; border-radius: 8px; background: #2b2b3a;} QProgressBar::chunk {background: #5bc0de;}")
        left_layout.addWidget(self.energy_bar)

        settings_group = QtWidgets.QGroupBox("Настройки")
        settings_group.setStyleSheet("QGroupBox {border: 1px solid #444; margin-top: 6px; padding: 10px;}")
        settings_layout = QtWidgets.QFormLayout(settings_group)
        settings_layout.setLabelAlignment(QtCore.Qt.AlignLeft)
        settings_layout.setFormAlignment(QtCore.Qt.AlignLeft)

        self.stop_hp_input = QtWidgets.QSpinBox()
        self.stop_hp_input.setRange(0, 20000)
        self.stop_hp_input.setValue(DEFAULT_STOP_HP)
        settings_layout.addRow("Stop HP:", self.stop_hp_input)

        self.stim_energy_input = QtWidgets.QSpinBox()
        self.stim_energy_input.setRange(0, 1000)
        self.stim_energy_input.setValue(DEFAULT_STIM_ENERGY)
        settings_layout.addRow("Stim energy limit:", self.stim_energy_input)

        self.auto_stim_checkbox = QtWidgets.QCheckBox("Авто стимуляторы")
        self.auto_stim_checkbox.setChecked(True)
        settings_layout.addRow(self.auto_stim_checkbox)

        self.auto_connect_checkbox = QtWidgets.QCheckBox("Подключаться к рейдам")
        self.auto_connect_checkbox.setChecked(True)
        settings_layout.addRow(self.auto_connect_checkbox)

        self.connect_lornet_checkbox = QtWidgets.QCheckBox("Только Лорнет")
        self.connect_lornet_checkbox.setChecked(True)
        settings_layout.addRow(self.connect_lornet_checkbox)

        self.shout_checkbox = QtWidgets.QCheckBox("Звать игроков в бой")
        settings_layout.addRow(self.shout_checkbox)

        left_layout.addWidget(settings_group)

        login_group = QtWidgets.QGroupBox("Telegram auth")
        login_group.setStyleSheet("QGroupBox {border: 1px solid #444; margin-top: 6px; padding: 10px;}")
        login_layout = QtWidgets.QVBoxLayout(login_group)
        self.telegram_input = QtWidgets.QLineEdit()
        self.telegram_input.setPlaceholderText("Вставьте initData Telegram сюда")
        self.telegram_input.setStyleSheet("QLineEdit {background: #2b2b3a; border: 1px solid #444; color: #e6e6e6; padding: 6px;}")
        login_layout.addWidget(self.telegram_input)
        left_layout.addWidget(login_group)
        left_layout.addStretch(1)

        layout.addWidget(left_panel)

        central_panel = QtWidgets.QFrame()
        central_layout = QtWidgets.QVBoxLayout(central_panel)
        central_layout.setSpacing(12)

        status_bar = QtWidgets.QHBoxLayout()
        self.raid_label = QtWidgets.QLabel("Рейд: —")
        self.raid_label.setStyleSheet("font-size: 14px; color: #b7b7ff;")
        self.boss_label = QtWidgets.QLabel("BOSS HP: —")
        self.boss_label.setStyleSheet("font-size: 14px; color: #ffc107;")
        self.status_label = QtWidgets.QLabel("Статус: остановлено")
        self.status_label.setStyleSheet("font-size: 14px; color: #d9d9d9;")
        status_bar.addWidget(self.raid_label)
        status_bar.addWidget(self.boss_label)
        status_bar.addStretch(1)
        status_bar.addWidget(self.status_label)
        central_layout.addLayout(status_bar)

        self.log_edit = QtWidgets.QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setStyleSheet("QTextEdit {background: #151520; border: 1px solid #444; color: #e6e6e6;}")
        central_layout.addWidget(self.log_edit, 1)

        bottom_panel = QtWidgets.QFrame()
        bottom_panel.setStyleSheet("border: 1px solid #444; background: #1f1f2d;")
        bottom_layout = QtWidgets.QHBoxLayout(bottom_panel)
        bottom_layout.setContentsMargins(12, 10, 12, 10)

        self.stats_label = QtWidgets.QLabel("XP: 0 | GOLD: 0 | BUCKS: 0 | STIMS: 0")
        self.stats_label.setStyleSheet("color: #aab7ff;")
        bottom_layout.addWidget(self.stats_label)
        bottom_layout.addStretch(1)

        self.start_button = QtWidgets.QPushButton("START")
        self.start_button.setStyleSheet("QPushButton {background: #3f8cfd; color: white; padding: 10px 22px; border-radius: 8px;} QPushButton:hover {background: #66a8ff;}")
        bottom_layout.addWidget(self.start_button)
        self.stop_button = QtWidgets.QPushButton("STOP")
        self.stop_button.setStyleSheet("QPushButton {background: #8c3f3f; color: white; padding: 10px 22px; border-radius: 8px;} QPushButton:hover {background: #b35f5f;}")
        self.stop_button.setEnabled(False)
        bottom_layout.addWidget(self.stop_button)

        central_layout.addWidget(bottom_panel)
        layout.addWidget(central_panel, 1)

    def _connect_signals(self) -> None:
        self.start_button.clicked.connect(self.on_start)
        self.stop_button.clicked.connect(self.on_stop)
        self.manager.log_signal.connect(self.append_log)
        self.manager.status_signal.connect(self.set_status)
        self.manager.hp_signal.connect(self.update_hp)
        self.manager.energy_signal.connect(self.update_energy)
        self.manager.boss_hp_signal.connect(self.update_boss_hp)
        self.manager.raid_signal.connect(self.set_raid)
        self.manager.stats_signal.connect(self.update_stats)
        self.manager.running_signal.connect(self.on_running_changed)

    def on_start(self) -> None:
        init_data = self.telegram_input.text().strip()
        if not init_data:
            self.append_log("Telegram initData нужен для логина")
            return
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.manager.set_settings(
            stop_hp=self.stop_hp_input.value(),
            stim_energy=self.stim_energy_input.value(),
            auto_stimulants=self.auto_stim_checkbox.isChecked(),
            auto_raids=self.auto_connect_checkbox.isChecked(),
            only_lornet=self.connect_lornet_checkbox.isChecked(),
            shout=self.shout_checkbox.isChecked(),
        )
        self.append_log("Запуск менеджера...")
        asyncio.create_task(self.manager.start(init_data))

    def on_stop(self) -> None:
        self.append_log("Останавливаем...")
        asyncio.create_task(self.manager.stop())

    def append_log(self, text: str) -> None:
        self.log_edit.append(text)
        self.log_edit.verticalScrollBar().setValue(self.log_edit.verticalScrollBar().maximum())

    def set_status(self, text: str) -> None:
        self.status_label.setText(f"Статус: {text}")

    def set_raid(self, raid_text: str) -> None:
        self.raid_label.setText(f"Рейд: {raid_text}")

    def update_hp(self, current: int, maximum: int) -> None:
        self.hp_bar.setMaximum(maximum or 1)
        self.hp_bar.setValue(current)
        self.hp_bar.setFormat(f"HP: {current} / {maximum}")

    def update_energy(self, current: int, maximum: int) -> None:
        self.energy_bar.setMaximum(maximum or 1)
        self.energy_bar.setValue(current)
        self.energy_bar.setFormat(f"Energy: {current} / {maximum}")

    def update_boss_hp(self, current: int, maximum: int) -> None:
        self.boss_label.setText(f"BOSS HP: {current} / {maximum}")

    def update_stats(self, stats: dict) -> None:
        xp = stats.get("xp", 0)
        gold = stats.get("gold", 0)
        bucks = stats.get("bucks", 0)
        stims = stats.get("stimulants", 0)
        self.stats_label.setText(f"XP: {xp} | GOLD: {gold} | BUCKS: {bucks} | STIMS: {stims}")

    def on_running_changed(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
