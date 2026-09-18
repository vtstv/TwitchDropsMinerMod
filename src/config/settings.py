from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from yarl import URL

from src.config import DEFAULT_LANG, SETTINGS_PATH
from src.utils import DropIgnorePolicy, json_load, json_save


class InventoryFilters(TypedDict):
    game_name_search: list[str]
    show_active: bool
    show_benefit_badge: bool
    show_benefit_emote: bool
    show_benefit_item: bool
    show_benefit_other: bool
    show_expired: bool
    show_finished: bool
    show_only_not_linked: bool
    show_upcoming: bool


default_settings = {
    "connection_quality": 1,
    "dark_mode": False,
    "drop_name_blacklist": [],
    "games_to_watch": [],
    "language": DEFAULT_LANG,
    "inventory_filters": {
        "game_name_search": [],
        "show_active": False,
        "show_benefit_badge": True,
        "show_benefit_emote": True,
        "show_benefit_item": True,
        "show_benefit_other": True,
        "show_expired": False,
        "show_finished": False,
        "show_only_not_linked": False,
        "show_upcoming": True,
    },
    "inventory_list_view": False,
    "minimum_refresh_interval_minutes": 30,
    "mining_benefits": {
        "BADGE": True,
        "DIRECT_ENTITLEMENT": True,
        "EMOTE": True,
        "UNKNOWN": True,
    },
    "proxy": "",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
    "auto_reload_campaigns": True,
    "campaign_reload_interval_minutes": 60,
    "auto_add_new_games": True,
    "mine_unlinked_campaigns": False,
    "randomize_behavior": True,
    "random_jitter_seconds": 5,
    "random_switch_delay": 10,
    "random_breaks_enabled": False,
    "random_break_interval_hours": 3,
    "random_break_duration_minutes": 5,
}


@dataclass
class Settings:
    connection_quality: int = 1
    dark_mode: bool = False
    drop_name_blacklist: list[str] = None
    games_to_watch: list[str] = None
    language: str = DEFAULT_LANG
    inventory_filters: InventoryFilters = None
    inventory_list_view: bool = False
    minimum_refresh_interval_minutes: int = 30
    mining_benefits: dict[str, bool] = None
    proxy: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    auto_reload_campaigns: bool = True
    campaign_reload_interval_minutes: int = 60
    auto_add_new_games: bool = True
    mine_unlinked_campaigns: bool = False
    randomize_behavior: bool = True
    random_jitter_seconds: int = 5
    random_switch_delay: int = 10
    random_breaks_enabled: bool = False
    random_break_interval_hours: int = 3
    random_break_duration_minutes: int = 5

    def __init__(self):
        self.load()

    def load(self):
        # TODO: remvoe customized serde in the future
        settings = json_load(SETTINGS_PATH, default_settings, merge=True)
        for key, value in settings.items():
            if value is URL:
                setattr(self, key, str(value))
            else:
                setattr(self, key, value)
        self.drop_name_blacklist = DropIgnorePolicy.normalize_keywords(
            self.drop_name_blacklist
        )

    def save(self) -> None:
        self.drop_name_blacklist = DropIgnorePolicy.normalize_keywords(
            self.drop_name_blacklist
        )
        json_save(SETTINGS_PATH, vars(self), sort=True)
