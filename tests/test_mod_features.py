import asyncio
import contextlib
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from src.config.settings import Settings, default_settings
from src.models.campaign import DropsCampaign
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
            self.assertFalse(settings.mine_unlinked_campaigns)
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
            "mine_unlinked_campaigns": True,
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
        self.assertTrue(model.mine_unlinked_campaigns)
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
        self.assertTrue(result["mine_unlinked_campaigns"])
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
        settings.mine_unlinked_campaigns = False
        settings.save = MagicMock()

        # Mock inventory campaigns
        campaign_a = MagicMock()
        campaign_a.can_be_mined = True
        campaign_a.expired = False
        campaign_a.game = Game({"id": 1, "name": "Game A"})

        # Game B is linked and active - should be added
        campaign_b = MagicMock()
        campaign_b.can_be_mined = True
        campaign_b.expired = False
        campaign_b.game = Game({"id": 2, "name": "Game B"})

        # Game C is NOT eligible (unlinked account, mine_unlinked=False) - should NOT be added
        campaign_c = MagicMock()
        campaign_c.can_be_mined = False
        campaign_c.expired = False
        campaign_c.game = Game({"id": 3, "name": "Game C"})

        # Game D is expired - should NOT be added
        campaign_d = MagicMock()
        campaign_d.can_be_mined = True
        campaign_d.expired = True
        campaign_d.game = Game({"id": 4, "name": "Game D"})

        inventory = [campaign_a, campaign_b, campaign_c, campaign_d]

        # Check behavior when mine_unlinked_campaigns is False
        existing_lower = {g.lower() for g in settings.games_to_watch}
        added_games = []
        for campaign in inventory:
            if (
                campaign.can_be_mined
                and campaign.game
                and campaign.game.name
                and not campaign.expired
                and campaign.game.name.lower() not in existing_lower
            ):
                settings.games_to_watch.append(campaign.game.name)
                existing_lower.add(campaign.game.name.lower())
                added_games.append(campaign.game.name)

        self.assertIn("Game B", settings.games_to_watch)
        self.assertNotIn("Game C", settings.games_to_watch)
        self.assertNotIn("Game D", settings.games_to_watch)
        self.assertEqual(added_games, ["Game B"])

        # Now test when mine_unlinked_campaigns is True: Game C's can_be_mined becomes True
        campaign_c.can_be_mined = True
        added_games_unlinked = []
        for campaign in inventory:
            if (
                campaign.can_be_mined
                and campaign.game
                and campaign.game.name
                and not campaign.expired
                and campaign.game.name.lower() not in existing_lower
            ):
                settings.games_to_watch.append(campaign.game.name)
                existing_lower.add(campaign.game.name.lower())
                added_games_unlinked.append(campaign.game.name)

        self.assertIn("Game C", settings.games_to_watch)
        self.assertEqual(added_games_unlinked, ["Game C"])

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
        old_time = service._last_break_time - 100
        service._last_break_time = old_time
        service.reset_break_timer()
        self.assertGreater(service._last_break_time, old_time)

    def test_resume_mining_resets_break_timer(self):
        from src.core.client import Twitch
        twitch = MagicMock(spec=Twitch)
        twitch.mining_enabled = False
        twitch._watch_service = MagicMock()
        twitch.gui = MagicMock()
        Twitch.resume_mining(twitch)
        self.assertTrue(twitch.mining_enabled)
        twitch._watch_service.reset_break_timer.assert_called_once()
        twitch.gui.status.update.assert_called_with("▶ Resuming mining...")

    def test_drops_campaign_can_be_mined(self):
        twitch = MagicMock()
        twitch.settings = SimpleNamespace(mine_unlinked_campaigns=False)

        campaign_data = {
            "id": "camp1",
            "name": "Test Campaign",
            "game": {"id": 10, "name": "Game X"},
            "self": {"isAccountConnected": False},
            "accountLinkURL": "https://example.com/link",
            "startAt": "2026-09-18T00:00:00Z",
            "endAt": "2026-09-19T00:00:00Z",
            "status": "ACTIVE",
            "allow": {"channels": [], "isEnabled": True},
            "timeBasedDrops": [],
        }

        campaign = DropsCampaign(twitch, campaign_data, {})
        self.assertFalse(campaign.eligible)
        self.assertFalse(campaign.can_be_mined)

        twitch.settings.mine_unlinked_campaigns = True
        self.assertFalse(campaign.eligible)
        self.assertTrue(campaign.can_be_mined)

    async def test_all_drops_games_settings_and_normalization(self):
        # Test normalization
        raw_games = ["  World of Warcraft  ", "", "  ", "rust", "RUST", "No Man's Sky  "]
        normalized = Settings.normalize_games_list(raw_games)
        self.assertEqual(normalized, ["World of Warcraft", "rust", "No Man's Sky"])

        # Test defaults
        with patch("src.config.settings.json_load", return_value={}):
            settings = Settings()
            self.assertEqual(settings.all_drops_games, [])

        # Test SettingsUpdate model
        model = SettingsUpdate(all_drops_games=["Rust", "WoW"])
        self.assertEqual(model.all_drops_games, ["Rust", "WoW"])

        # Test SettingsManager update
        settings_dict = copy.deepcopy(default_settings)
        settings_dict["all_drops_games"] = []
        settings = SimpleNamespace(**settings_dict)
        settings.save = MagicMock()
        broadcaster = AsyncMock()
        manager = SettingsManager(broadcaster, settings, MagicMock())

        result = manager.update_settings({"all_drops_games": ["  Game A ", "Game A", "Game B "]})
        self.assertEqual(result["all_drops_games"], ["Game A", "Game B"])
        self.assertEqual(settings.all_drops_games, ["Game A", "Game B"])
        settings.save.assert_called_once()

    def test_all_drops_games_stream_selector_and_filter_bypass(self):
        from datetime import datetime, timezone

        from src.core.client import Twitch
        from src.models.benefit import Benefit
        from src.services.stream_selector import StreamSelector

        settings = MagicMock(spec=Settings)
        settings.games_to_watch = ["Game Normal", "Game AllDrops"]
        settings.mining_benefits = {"DIRECT_ENTITLEMENT": False, "BADGE": True, "EMOTE": True, "UNKNOWN": True}
        settings.all_drops_games = ["Game AllDrops"]

        item_benefit = Benefit({
            "benefit": {
                "id": "b_item",
                "name": "Cool Sword",
                "distributionType": "DIRECT_ENTITLEMENT",
                "imageAssetURL": "https://example.com/item.png",
            }
        })

        # Campaign for Game Normal (only has item drop)
        camp_normal = MagicMock(spec=DropsCampaign)
        camp_normal.id = "c_normal"
        camp_normal.name = "Normal Campaign"
        camp_normal.campaign_url = "https://twitch.tv/camp_normal"
        camp_normal.game = Game({"id": 101, "name": "Game Normal"})
        camp_normal.can_earn_within.return_value = True

        drop_normal = MagicMock()
        drop_normal.name = "Normal Drop"
        drop_normal.is_watch_drop = True
        drop_normal.is_claimed = False
        drop_normal.ends_at = datetime.max.replace(tzinfo=timezone.utc)
        drop_normal.is_mineable = True
        drop_normal.benefits = [item_benefit]
        # Real get_wanted_unclaimed_benefits behavior
        drop_normal.get_wanted_unclaimed_benefits.side_effect = (
            lambda allowed: [b.name for b in drop_normal.benefits if b.is_wanted(allowed)]
        )
        drop_normal.has_wanted_unclaimed_benefits.side_effect = (
            lambda allowed: len(drop_normal.get_wanted_unclaimed_benefits(allowed)) > 0
        )
        camp_normal.drops = [drop_normal]
        camp_normal.has_wanted_unclaimed_benefits.side_effect = (
            lambda allowed: any(d.has_wanted_unclaimed_benefits(allowed) for d in camp_normal.drops)
        )

        # Campaign for Game AllDrops (also only has item drop)
        camp_all_drops = MagicMock(spec=DropsCampaign)
        camp_all_drops.id = "c_alldrops"
        camp_all_drops.name = "AllDrops Campaign"
        camp_all_drops.campaign_url = "https://twitch.tv/camp_alldrops"
        camp_all_drops.game = Game({"id": 102, "name": "Game AllDrops"})
        camp_all_drops.can_earn_within.return_value = True

        drop_all_drops = MagicMock()
        drop_all_drops.name = "AllDrops Item Drop"
        drop_all_drops.is_watch_drop = True
        drop_all_drops.is_claimed = False
        drop_all_drops.ends_at = datetime.max.replace(tzinfo=timezone.utc)
        drop_all_drops.is_mineable = True
        drop_all_drops.benefits = [item_benefit]
        drop_all_drops.get_wanted_unclaimed_benefits.side_effect = (
            lambda allowed: [b.name for b in drop_all_drops.benefits if b.is_wanted(allowed)]
        )
        drop_all_drops.has_wanted_unclaimed_benefits.side_effect = (
            lambda allowed: len(drop_all_drops.get_wanted_unclaimed_benefits(allowed)) > 0
        )
        camp_all_drops.drops = [drop_all_drops]
        camp_all_drops.has_wanted_unclaimed_benefits.side_effect = (
            lambda allowed: any(d.has_wanted_unclaimed_benefits(allowed) for d in camp_all_drops.drops)
        )

        inventory = [camp_normal, camp_all_drops]
        selector = StreamSelector()
        wanted_tree = selector.get_wanted_game_tree(settings, inventory)
        wanted_games = selector.get_wanted_games(settings, inventory)

        # Game Normal should be excluded because DIRECT_ENTITLEMENT is False globally and not in all_drops_games
        # Game AllDrops should be INCLUDED because it is in all_drops_games
        self.assertEqual(len(wanted_games), 1)
        self.assertEqual(wanted_games[0].name, "Game AllDrops")
        self.assertEqual(len(wanted_tree), 1)
        self.assertEqual(wanted_tree[0]["game_name"], "Game AllDrops")
        self.assertEqual(wanted_tree[0]["campaigns"][0]["drops"][0]["benefits"], ["Cool Sword"])

        # Also test Twitch._filter_wanted_campaigns
        twitch = MagicMock(spec=Twitch)
        twitch.settings = settings
        twitch.inventory = inventory
        next_hour = datetime.now(timezone.utc)
        filtered_games = Twitch._filter_wanted_campaigns(twitch, next_hour)
        self.assertEqual(len(filtered_games), 1)
        self.assertEqual(filtered_games[0].name, "Game AllDrops")
