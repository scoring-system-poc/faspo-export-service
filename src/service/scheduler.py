import logging
import asyncio
import schedule

from src.core.config import CONFIG, Export
from src.service import exporter


logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(self):
        self._is_running: asyncio.Event = asyncio.Event()

    async def start(self) -> bool:
        """
        Start the scheduler.
        :return: True if the scheduler started successfully, False otherwise.
        """
        self._is_running.set()

        await self._schedule_exports()
        asyncio.ensure_future(self._run_scheduler())

        return self._is_running.is_set()

    async def _schedule_exports(self) -> None:
        """
        Schedule exports based on their schedule time.
        :return:
        """
        for export in CONFIG.EXPORT_SETUP:
            if not export.schedule_time:
                logger.info(f"export '{export.name}' has no schedule time and therefore must be triggered manually.")
                continue

            logger.info(f"export '{export.name}' is scheduled to run every day at {export.schedule_time}.")
            schedule.every().day.at(export.schedule_time).do(self._wrap_export_task_in_aio, export).tag(export.name)

    @staticmethod
    def _wrap_export_task_in_aio(export: Export) -> None:
        """
        Helper func that wraps the export task in an asyncio task to run it asynchronously.
        :param export: Export object containing export configuration
        :return:
        """
        asyncio.ensure_future(exporter.generate_export(export))

    async def _run_scheduler(self) -> None:
        """
        Run the scheduler to execute scheduled tasks.
        :return:
        """
        while self._is_running.is_set():
            schedule.run_pending()
            await asyncio.sleep(1)

    async def stop(self) -> bool:
        """
        Stop the scheduler.
        :return: True if the scheduler stopped successfully, False otherwise.
        """
        self._is_running.clear()
        return not self._is_running.is_set()

