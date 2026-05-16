import argparse
import asyncio
import os
import qasync
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
from battle_manager import BattleManager
from gui import MainWindow


def run_gui() -> None:
    app = QApplication([])
    window = MainWindow()
    window.show()
    
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    with loop:
        loop.run_forever()


def run_headless(init_data: str) -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QtCore.QCoreApplication([])
    manager = BattleManager()
    manager.log_signal.connect(lambda text: print(text))
    manager.status_signal.connect(lambda text: print(f"STATUS: {text}"))
    manager.hp_signal.connect(lambda cur, mx: print(f"HP: {cur}/{mx}"))
    manager.energy_signal.connect(lambda cur, mx: print(f"ENERGY: {cur}/{mx}"))
    manager.boss_hp_signal.connect(lambda cur, mx: print(f"BOSS HP: {cur}/{mx}"))
    manager.raid_signal.connect(lambda text: print(f"RAID: {text}"))
    manager.stats_signal.connect(lambda stats: print(f"STATS: XP={stats.get('xp')} GOLD={stats.get('gold')} BUCKS={stats.get('bucks')} STIMS={stats.get('stimulants')}"))
    manager.running_signal.connect(lambda running: print(f"RUNNING: {running}"))

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        loop.run_until_complete(manager.start(init_data))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Madness RPG desktop client")
    parser.add_argument("--headless", action="store_true", help="Run without GUI for headless testing")
    parser.add_argument("--init-data", type=str, help="Telegram initData for authentication")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.headless:
        if not args.init_data:
            raise SystemExit("--init-data required in headless mode")
        run_headless(args.init_data)
    else:
        run_gui()
