"""
Maintenance service for periodic inventory reloads and cleanup triggers.

This service manages scheduled tasks that trigger inventory fetches and channel cleanups
based on campaign timing (starts/ends) and hourly reload cycles.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from src.config import CALL, State
from src.utils import task_wrapper


if TYPE_CHECKING:
    from src.core.client import Twitch


logger = logging.getLogger("TwitchDrops")


class MaintenanceService:
    """
    Service responsible for periodic maintenance tasks.

    Handles:
    - Hourly inventory reloads
    - Campaign-triggered channel cleanups (when drops start/end)
    - Task scheduling based on time triggers
    """

    def __init__(self, twitch: Twitch) -> None:
        """
        Initialize the maintenance service.

        Args:
            twitch: The Twitch client instance
        """
        self._twitch = twitch

    @task_wrapper(critical=True)
    async def run_maintenance_task(self) -> None:
        """
        Execute the maintenance task loop.

        This task monitors time triggers for channel cleanup and performs
        periodic inventory reloads approximately every 60 minutes. The task
        exits after each reload cycle and is restarted by fetch_inventory.

        The maintenance logic:
        1. Wait until the next trigger (either a campaign time trigger or next hour)
        2. If the trigger is a campaign timing change, request channel cleanup
        3. After reaching the next hour boundary, request inventory reload
        """
        now = datetime.now(timezone.utc)
        auto_reload: bool = getattr(self._twitch.settings, "auto_reload_campaigns", True)
        if auto_reload:
            interval = getattr(
                self._twitch.settings,
                "campaign_reload_interval_minutes",
                self._twitch.settings.minimum_refresh_interval_minutes,
            )
            next_period = now + timedelta(minutes=max(1, interval))
        else:
            # If periodic reload is disabled, wait indefinitely for campaign triggers
            next_period = now + timedelta(days=365)

        while True:
            now = datetime.now(timezone.utc)
            if auto_reload and now >= next_period:
                break

            next_trigger = next_period
            while self._twitch._mnt_triggers and self._twitch._mnt_triggers[0] <= next_trigger:
                next_trigger = self._twitch._mnt_triggers.popleft()

            trigger_type: str = "Reload" if next_trigger == next_period else "Cleanup"
            logger.log(
                CALL,
                (
                    "Maintenance task waiting until: "
                    f"{next_trigger.astimezone().strftime('%X')} ({trigger_type})"
                ),
            )

            await asyncio.sleep(max(0.1, (next_trigger - now).total_seconds()))

            # exit after waiting, before the actions
            now = datetime.now(timezone.utc)
            if auto_reload and now >= next_period:
                break

            if next_trigger != next_period:
                logger.log(CALL, "Maintenance task requests channels cleanup")
                self._twitch.change_state(State.CHANNELS_CLEANUP)

        if auto_reload:
            # this triggers a restart of this task every <campaign_reload_interval_minutes> minutes
            logger.log(CALL, "Maintenance task requests a reload")
            self._twitch.request_inventory_refresh()
