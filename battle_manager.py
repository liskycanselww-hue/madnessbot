import asyncio
from typing import Any, Dict, List, Optional
from PyQt5.QtCore import QObject, pyqtSignal
from api import ApiClient, ApiError
from config import DEFAULT_STOP_HP, DEFAULT_STIM_ENERGY, TARGET_PLAYER


class BattleManager(QObject):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    hp_signal = pyqtSignal(int, int)
    boss_hp_signal = pyqtSignal(int, int)
    energy_signal = pyqtSignal(int, int)
    raid_signal = pyqtSignal(str)
    stats_signal = pyqtSignal(dict)
    running_signal = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.api = ApiClient()
        self.running = False
        self.settings = {
            "stop_hp": DEFAULT_STOP_HP,
            "stim_energy": DEFAULT_STIM_ENERGY,
            "auto_stimulants": True,
            "auto_raids": True,
            "only_lornet": True,
            "shout": False,
        }
        self.stats = {"xp": 0, "gold": 0, "bucks": 0, "stimulants": 0}
        self.current_raid: Optional[Dict[str, Any]] = None
        self.character_id: Optional[str] = None
        self.token: Optional[str] = None

    def set_settings(
        self,
        stop_hp: int,
        stim_energy: int,
        auto_stimulants: bool,
        auto_raids: bool,
        only_lornet: bool,
        shout: bool,
    ) -> None:
        self.settings.update(
            stop_hp=stop_hp,
            stim_energy=stim_energy,
            auto_stimulants=auto_stimulants,
            auto_raids=auto_raids,
            only_lornet=only_lornet,
            shout=shout,
        )

    def log(self, message: str) -> None:
        self.log_signal.emit(message)

    def status(self, message: str) -> None:
        self.status_signal.emit(message)

    async def start(self, init_data: str) -> None:
        if self.running:
            return
        self.running = True
        self.running_signal.emit(True)
        self.log("Логинимся...")
        try:
            login_data = await self.api.login(init_data)
            token = login_data.get("token") or login_data.get("access_token")
            character_id = (
                login_data.get("character_id")
                or login_data.get("characterId")
                or (login_data.get("user") or {}).get("id")
                or (login_data.get("user") or {}).get("telegram_id")
            )
            if not token or not character_id:
                raise ApiError("Не удалось получить token или character_id после логина")
            self.api.token = token
            self.character_id = str(character_id)
            self.token = token
            self.log("Успешный логин")
            await self._main_loop()
        except Exception as exc:
            self.log(f"Ошибка логина: {exc}")
        finally:
            self.running = False
            self.running_signal.emit(False)
            self.status("Остановлено")
            await self.api.close()

    async def stop(self) -> None:
        self.running = False
        self.status("Остановка...")

    async def _main_loop(self) -> None:
        while self.running:
            try:
                character = await self._refresh_character()
                self._publish_character(character)
                self.status("Ищем рейд")
                raid = await self._select_raid()
                if raid is None:
                    self.log("Рейд не найден, повторяем поиск через 5 секунд")
                    await asyncio.sleep(5)
                    continue
                await self._process_raid(raid)
            except Exception as exc:
                self.log(f"Ошибка в цикле: {exc}")
                await asyncio.sleep(4)

    async def _refresh_character(self) -> Dict[str, Any]:
        if not self.character_id:
            raise ApiError("character_id не задан")
        data = await self.api.get_character(self.character_id)
        derived = data.get("derived", {})
        return {
            "hp": int(derived.get("hp", 0)),
            "max_hp": int(derived.get("max_hp", 0)),
            "energy": int(data.get("energy", 0)),
            "max_energy": int(data.get("max_energy", 0)),
            "xp": int(data.get("xp", 0)),
            "gold": int(data.get("gold", 0)),
            "bucks": int(data.get("bucks", 0)),
            "level": int(data.get("level", 0)),
            "stimulants_used": int(data.get("stimulants_used", 0)),
        }

    def _publish_character(self, character: Dict[str, Any]) -> None:
        self.hp_signal.emit(character["hp"], character["max_hp"])
        self.energy_signal.emit(character["energy"], character["max_energy"])

    async def _select_raid(self) -> Optional[Dict[str, Any]]:
        raids = await self.api.get_raids()
        active_raids = [r for r in raids if self._is_active_raid(r)]
        if not active_raids:
            return None
        if self.settings["only_lornet"]:
            lornet = [r for r in active_raids if self._raid_owner_name(r) == TARGET_PLAYER]
            if lornet:
                return lornet[0]
            if self.settings["auto_raids"]:
                return active_raids[0]
            return None
        if self.settings["auto_raids"]:
            return active_raids[0]
        return None

    def _is_active_raid(self, raid: Dict[str, Any]) -> bool:
        if isinstance(raid.get("status"), str):
            return raid["status"].lower() in ("active", "started", "running")
        return raid.get("active", False) is True

    def _raid_owner_name(self, raid: Dict[str, Any]) -> str:
        owner = raid.get("owner") or raid.get("player") or raid.get("host") or {}
        if isinstance(owner, dict):
            return owner.get("nickname") or owner.get("name") or ""
        if isinstance(owner, str):
            return owner
        return ""

    def _raid_label(self, raid: Dict[str, Any]) -> str:
        owner = self._raid_owner_name(raid)
        raid_id = raid.get("id") or raid.get("raid_id") or "—"
        boss = raid.get("boss", {})
        boss_name = boss.get("name") or boss.get("title") or "boss"
        return f"{owner} | {boss_name} | {raid_id}"

    async def _process_raid(self, raid: Dict[str, Any]) -> None:
        raid_text = self._raid_label(raid)
        self.current_raid = raid
        self.raid_signal.emit(raid_text)
        self.log(f"Подключились к рейду {raid_text}")
        if self.settings["shout"]:
            await self._send_shout(raid)
        await self._battle_loop(raid)

    async def _send_shout(self, raid: Dict[str, Any]) -> None:
        raid_id = str(raid.get("id") or raid.get("raid_id") or "")
        if not raid_id:
            return
        try:
            await self.api.shout_to_raid(raid_id, "Вперед, команда! Заходим в бой!")
            self.log("Отправлено приглашение в рейд")
        except Exception as exc:
            self.log(f"Не удалось позвать игроков: {exc}")

    async def _battle_loop(self, raid: Dict[str, Any]) -> None:
        raid_id = str(raid.get("id") or raid.get("raid_id") or "")
        while self.running:
            try:
                battle = await self.api.get_current_battle()
                if not battle:
                    self.log("Нет текущей битвы, ждем...")
                    await asyncio.sleep(3)
                    continue
                player_hp, player_max_hp, energy, energy_max = self._parse_character_state(battle)
                boss_hp, boss_max_hp = self._parse_boss_state(battle)
                self.hp_signal.emit(player_hp, player_max_hp)
                self.energy_signal.emit(energy, energy_max)
                self.boss_hp_signal.emit(boss_hp, boss_max_hp)
                self.status("В бою")
                if player_hp <= self.settings["stop_hp"]:
                    self.log(f"HP ниже лимита ({player_hp} <= {self.settings['stop_hp']})")
                    self.status("Ожидаем добивание")
                    if boss_hp <= 0:
                        await self._claim_reward()
                        return
                    await asyncio.sleep(5)
                    continue
                if self.settings["auto_stimulants"] and energy <= self.settings["stim_energy"]:
                    await self._use_stimulant()
                if boss_hp <= 0:
                    self.log("Босс побежден")
                    await self._claim_reward()
                    return
                await self._attack(raid_id)
                await asyncio.sleep(2)
            except Exception as exc:
                self.log(f"Ошибка битвы: {exc}")
                await asyncio.sleep(3)

    def _parse_character_state(self, battle: Dict[str, Any]) -> List[int]:
        source = battle.get("character") or battle.get("player") or battle.get("self") or battle
        hp = int(source.get("hp") or source.get("current_hp") or 0)
        max_hp = int(source.get("max_hp") or source.get("maxHp") or source.get("hp_max") or hp)
        energy = int(source.get("energy") or source.get("stamina") or 0)
        max_energy = int(source.get("max_energy") or source.get("maxEnergy") or source.get("stamina_max") or energy)
        return hp, max_hp, energy, max_energy

    def _parse_boss_state(self, battle: Dict[str, Any]) -> List[int]:
        boss = battle.get("boss") or battle.get("enemy") or {}
        hp = int(boss.get("hp") or boss.get("current_hp") or 0)
        max_hp = int(boss.get("max_hp") or boss.get("maxHp") or boss.get("hp_max") or hp)
        return hp, max_hp

    async def _attack(self, raid_id: str) -> None:
        if not raid_id:
            self.log("Нет raid_id для атаки")
            return
        self.log("Атака...")
        await self.api.attack(raid_id)

    async def _use_stimulant(self) -> None:
        if not self.character_id:
            return
        try:
            self.log("Использован стимулятор")
            await self.api.use_stimulant(self.character_id)
            self.stats["stimulants"] += 1
            self.stats_signal.emit(self.stats.copy())
        except Exception as exc:
            self.log(f"Ошибка стимулятора: {exc}")

    async def _claim_reward(self) -> None:
        try:
            reward = await self.api.claim_reward()
            self.log("Награда получена")
            self._update_reward_stats(reward)
            self.stats_signal.emit(self.stats.copy())
        except Exception as exc:
            self.log(f"Ошибка получения награды: {exc}")

    def _update_reward_stats(self, reward: Dict[str, Any]) -> None:
        xp = int(reward.get("xp") or reward.get("experience") or 0)
        gold = int(reward.get("gold") or reward.get("coins") or 0)
        bucks = int(reward.get("bucks") or reward.get("money") or 0)
        self.stats["xp"] += xp
        self.stats["gold"] += gold
        self.stats["bucks"] += bucks
        self.stats["stimulants"] = self.stats.get("stimulants", 0)
        if xp or gold or bucks:
            self.log(f"XP: +{xp} | GOLD: +{gold} | BUCKS: +{bucks}")
