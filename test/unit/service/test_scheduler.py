import pytest
import unittest.mock


@pytest.mark.asyncio
async def test_init():
    from src.service.scheduler import Scheduler
    assert not Scheduler()._is_running.is_set()


@pytest.mark.asyncio
async def test_start_stop():
    from src.service.scheduler import Scheduler
    scheduler = Scheduler()

    assert await scheduler.start()
    assert scheduler._is_running.is_set()

    assert await scheduler.stop()
    assert not scheduler._is_running.is_set()


@pytest.mark.asyncio
async def test_schedule_exports():
    with unittest.mock.patch("src.service.scheduler.schedule") as mock_schedule:
        from src.service.scheduler import Scheduler
        from src.core.config import CONFIG
        scheduler = Scheduler()

        await scheduler._schedule_exports()

        mock_schedule.every().day.at.assert_called_once_with("00:00")
        mock_schedule.every().day.at.return_value.do.assert_called_once_with(
            scheduler._wrap_export_task_in_aio, CONFIG.EXPORT_SETUP[0],
        )


@pytest.mark.asyncio
async def test_wrap_export_task_in_aio():
    from src.service.scheduler import Scheduler

    with (
        unittest.mock.patch("src.service.scheduler.asyncio") as mock_asyncio,
        unittest.mock.patch("src.service.scheduler.exporter") as mock_exporter,
    ):
        export = unittest.mock.Mock()
        Scheduler._wrap_export_task_in_aio(export)
        mock_asyncio.ensure_future.assert_called_once_with(mock_exporter.generate_export(export))


@pytest.mark.asyncio
async def test_run_scheduler():
    with unittest.mock.patch("src.service.scheduler.schedule") as mock_schedule:
        from src.service.scheduler import Scheduler
        scheduler = Scheduler()

        mock_schedule.run_pending.side_effect = lambda: scheduler._is_running.clear()

        scheduler._is_running.set()
        await scheduler._run_scheduler()

        assert mock_schedule.run_pending.called

