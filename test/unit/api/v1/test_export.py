import pytest
import unittest.mock
import httpx

from src.core.exception import HTTPException


@pytest.mark.asyncio
async def test_foo_export__success(async_client: httpx.AsyncClient) -> None:
    with unittest.mock.patch("src.api.v1.export.exporter") as mock_exporter:
        mock_exporter.generate_export = unittest.mock.AsyncMock()

        response = await async_client.post("/api/v1/export/foo")

        assert response.status_code == 200
        assert response.json() == {"detail": "Export generated successfully"}


@pytest.mark.asyncio
async def test_foo_export__failure(async_client: httpx.AsyncClient) -> None:
    with unittest.mock.patch("src.api.v1.export.exporter") as mock_exporter:
        mock_exporter.generate_export.side_effect = HTTPException(500)

        response = await async_client.post("/api/v1/export/foo")

        assert response.status_code == 500
        assert response.json() == {"detail": "Internal Server Error"}
