import typing
import logging
import fastapi
import datetime as dt

from src.core.config import CONFIG
from src.service import exporter


logger = logging.getLogger(__name__)
router = fastapi.APIRouter(
    prefix="/export",
    tags=["export"]
)


@router.post("/foo")
async def export_foo(
    date_from: typing.Annotated[dt.datetime, fastapi.Body()] = None,
    date_to: typing.Annotated[dt.datetime, fastapi.Body()] = None,
    correlation_id: typing.Annotated[str | None, fastapi.Header()] = None,
) -> fastapi.responses.JSONResponse:
    """
    Generate export for imaginary 'foo' system
    :param date_from: Date from which to export data
    :param date_to: Date to which to export data
    :param correlation_id: Correlation ID for logging
    :return: JSON response indicating success or failure
    """
    export_info = next(export for export in CONFIG.EXPORT_SETUP if export.name == "foo")
    await exporter.generate_export(export_info, date_from, date_to)
    return fastapi.responses.JSONResponse(status_code=200, content={"detail": "Export generated successfully"})
