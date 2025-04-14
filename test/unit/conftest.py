import pytest
import unittest.mock

import os
import azure.cosmos.aio
import azure.cosmos.exceptions


class _AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture(autouse=True)
def mock_environ(monkeypatch) -> None:
    with unittest.mock.patch.dict(os.environ, clear=True):
        env = {
            "AZURE_CLIENT_ID": "00000000-0000-0000-0000-000000000000",
            "AZURE_TENANT_ID": "00000000-0000-0000-0000-000000000000",
            "AZURE_SUBSCRIPTION_ID": "00000000-0000-0000-0000-000000000000",
            "COSMOS_URL": "https://test.documents.azure.com:443/",
            "COSMOS_DB": "test",
            "EXPORT_SETUP": '['
                            '{"name": "foo", "doc_types": ["foo"], "schedule_time": "00:00"},'
                            '{"name": "bar", "doc_types": ["bar"], "schedule_time": null}'
                            ']',
        }
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        yield


@pytest.fixture(autouse=True, scope="session")
def mock_cosmos() -> azure.cosmos.aio.DatabaseProxy:
    with (
        unittest.mock.patch("azure.identity.aio.WorkloadIdentityCredential"),
        unittest.mock.patch("azure.cosmos.aio.CosmosClient") as mock_client,
    ):
        mock_db = unittest.mock.AsyncMock(spec=azure.cosmos.aio.DatabaseProxy)
        mock_container = unittest.mock.AsyncMock(spec=azure.cosmos.aio.ContainerProxy)

        mock_container.query_items.return_value = _AsyncIterator([{"subject_id": "x", "sheets": [{"id": "sheet_id"}]}])
        mock_container.read_item.return_value = {"id": "sheet_id"}

        mock_db.get_container_client.return_value = mock_container

        mock_client.return_value = mock_client
        mock_client.get_database_client.return_value = mock_db

        yield mock_db

