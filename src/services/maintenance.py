"""
Maintenance service for periodic inventory reloads and cleanup triggers.

This service manages scheduled tasks that trigger inventory fetches and channel cleanups
based on campaign timing (starts/ends) and hourly reload cycles.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
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
        self._last_reload_time: datetime = datetime.now(timezone.utc)
        self._restart_event: asyncio.Event = asyncio.Event()

    def restart(self) -> None:
        """Signal the maintenance task to wake up and re-evaluate reload intervals immediately."""
        self._restart_event.set()

    def record_reload(self) -> None:
        """Record that an inventory reload occurred, resetting the reload timer."""
        self._last_reload_time = datetime.now(timezone.utc)

    async def _sleep(self, delay: float) -> None:
        """Sleep for a delay that can be interrupted by restart()."""
        self._restart_event.clear()
        with suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self._restart_event.wait(), timeout=delay)

    @task_wrapper(critical=True)
    async def run_maintenance_task(self) -> None:
        """
        Execute the maintenance task loop.

        This task monitors time triggers for channel cleanup and performs
        periodic inventory reloads approximately every 60 minutes. The task
        exits after each reload cycle and is restarted by fetch_inventory.

        The maintenance logic:
        1. Wait until the next trigger (either a campaign time trigger or next reload)
        2. If the trigger is a campaign timing change, request channel cleanup
        3. After reaching the reload boundary, request inventory reload
        """
        interval_minutes = self._twitch.settings.minimum_refresh_interval_minutes
        while True:
            now = datetime.now(timezone.utc)
            auto_reload: bool = getattr(self._twitch.settings, "auto_reload_campaigns", True)
            interval_minutes = getattr(
                self._twitch.settings,
                "campaign_reload_interval_minutes",
                self._twitch.settings.minimum_refresh_interval_minutes,
            )
            if auto_reload:
                next_period = self._last_reload_time + timedelta(
                    minutes=max(1, interval_minutes)
                )
                if now >= next_period:
                    break
            else:
                next_period = now + timedelta(days=365)

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

            sleep_duration = max(0.1, (next_trigger - now).total_seconds())
            await self._sleep(sleep_duration)

            if next_trigger != next_period and not self._restart_event.is_set():
                logger.log(CALL, "Maintenance task requests channels cleanup")
                self._twitch.change_state(State.CHANNELS_CLEANUP)

        if auto_reload:
            self.record_reload()
            reload_msg = f"🔄 Periodic campaign reload triggered (interval: {interval_minutes}m)"
            logger.info(reload_msg)
            self._twitch.print(reload_msg)
            self._twitch.request_inventory_refresh()
