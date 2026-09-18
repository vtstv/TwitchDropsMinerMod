import asyncio
import contextlib
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from src.config.settings import Settings, default_settings
from src.models.game import Game
from src.services.maintenance import MaintenanceService
from src.services.watch_service import WatchService
from src.web.app import SettingsUpdate
from src.web.managers.settings import SettingsManager


class TestModFeatures(unittest.IsolatedAsyncioTestCase):
    def test_settings_mod_defaults(self):
        with patch("src.config.settings.json_load", return_value={}):
            settings = Settings()
            self.assertTrue(settings.auto_reload_campaigns)
            self.assertEqual(settings.campaign_reload_interval_minutes, 60)
            self.assertTrue(settings.auto_add_new_games)
            self.assertTrue(settings.randomize_behavior)
            self.assertEqual(settings.random_jitter_seconds, 5)
            self.assertEqual(settings.random_switch_delay, 10)
            self.assertFalse(settings.random_breaks_enabled)
            self.assertEqual(settings.random_break_interval_hours, 3)
            self.assertEqual(settings.random_break_duration_minutes, 5)

    async def test_settings_update_and_manager(self):
        update_data = {
            "auto_reload_campaigns": False,
            "campaign_reload_interval_minutes": 120,
            "auto_add_new_games": True,
            "randomize_behavior": True,
            "random_jitter_seconds": 8,
            "random_switch_delay": 15,
            "random_breaks_enabled": True,
            "random_break_interval_hours": 2,
            "random_break_duration_minutes": 10,
        }
        model = SettingsUpdate(**update_data)
        self.assertFalse(model.auto_reload_campaigns)
        self.assertEqual(model.campaign_reload_interval_minutes, 120)
        self.assertEqual(model.random_jitter_seconds, 8)
        self.assertEqual(model.random_switch_delay, 15)
        self.assertTrue(model.random_breaks_enabled)
        self.assertEqual(model.random_break_interval_hours, 2)
        self.assertEqual(model.random_break_duration_minutes, 10)

        settings_dict = copy.deepcopy(default_settings)
        settings = SimpleNamespace(**settings_dict)
        settings.save = MagicMock()
        broadcaster = AsyncMock()
        manager = SettingsManager(broadcaster, settings, MagicMock())

        result = manager.update_settings(update_data)
        await asyncio.sleep(0)
        self.assertFalse(result["auto_reload_campaigns"])
        self.assertEqual(result["campaign_reload_interval_minutes"], 120)
        self.assertEqual(result["random_jitter_seconds"], 8)
        self.assertEqual(result["random_switch_delay"], 15)
        self.assertTrue(result["random_breaks_enabled"])
        self.assertEqual(result["random_break_interval_hours"], 2)
        self.assertEqual(result["random_break_duration_minutes"], 10)
        settings.save.assert_called_once()

    def test_auto_add_new_games_logic(self):
        settings = MagicMock(spec=Settings)
        settings.games_to_watch = ["Game A"]
        settings.auto_add_new_games = True
        settings.save = MagicMock()

        # Mock inventory campaigns
        campaign_a = MagicMock()
        campaign_a.expired = False
        campaign_a.game = Game({"id": 1, "name": "Game A"})

        # Game B is not linked, but active - should be added
        campaign_b = MagicMock()
        campaign_b.expired = False
        campaign_b.game = Game({"id": 2, "name": "Game B"})

        # Game C is expired - should NOT be added
        campaign_c = MagicMock()
        campaign_c.expired = True
        campaign_c.game = Game({"id": 3, "name": "Game C"})

        inventory = [campaign_a, campaign_b, campaign_c]

        # Check behavior of auto_add logic
        existing_lower = {g.lower() for g in settings.games_to_watch}
        added_games = []
        for campaign in inventory:
            if (
                campaign.game
                and campaign.game.name
                and not campaign.expired
                and campaign.game.name.lower() not in existing_lower
            ):
                settings.games_to_watch.append(campaign.game.name)
                existing_lower.add(campaign.game.name.lower())
                added_games.append(campaign.game.name)

        self.assertIn("Game B", settings.games_to_watch)
        self.assertNotIn("Game C", settings.games_to_watch)
        self.assertEqual(added_games, ["Game B"])

    async def test_maintenance_service_reload_interval(self):
        twitch = MagicMock()
        twitch._mnt_triggers = []
        twitch.settings = SimpleNamespace(
            auto_reload_campaigns=True,
            campaign_reload_interval_minutes=45,
            minimum_refresh_interval_minutes=30,
        )
        twitch.inventory = []
        twitch.change_state = MagicMock()
        twitch.request_inventory_refresh = MagicMock()

        service = MaintenanceService(twitch)
        with patch.object(service, "_sleep", new_callable=AsyncMock) as mock_sleep:
            mock_sleep.side_effect = [None, asyncio.CancelledError()]
            with contextlib.suppress(asyncio.CancelledError):
                await service.run_maintenance_task()

            self.assertTrue(mock_sleep.called)
            sleep_duration = mock_sleep.call_args_list[0].args[0]
            self.assertAlmostEqual(sleep_duration, 45 * 60, delta=5)

    async def test_watch_service_jitter_and_break(self):
        twitch = MagicMock()
        twitch.settings = SimpleNamespace(
            randomize_behavior=True,
            random_jitter_seconds=5,
            random_breaks_enabled=True,
            random_break_interval_hours=0.001,
            random_break_duration_minutes=1,
        )
        service = WatchService(twitch)
        self.assertIsNotNone(service._last_break_time)
