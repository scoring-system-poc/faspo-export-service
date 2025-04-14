import asyncio
import typing
import datetime as dt
import azure.cosmos.aio
import azure.identity.aio

from src.core.config import CONFIG


client = azure.cosmos.aio.CosmosClient(
    url=CONFIG.COSMOS_URL,
    credential=azure.identity.aio.WorkloadIdentityCredential(
        tenant_id=CONFIG.AZURE_TENANT_ID,
        client_id=CONFIG.AZURE_CLIENT_ID,
        token_file_path=CONFIG.AZURE_FEDERATED_TOKEN_FILE,
    ),
)

db = client.get_database_client(
    database=CONFIG.COSMOS_DB,
)

c_document = db.get_container_client(
    container=CONFIG.COSMOS_DOCUMENT_CONTAINER,
)


async def get_export_data(
    doc_types: list[str],
    date_from: dt.datetime | None = None,
    date_to: dt.datetime | None = None,
) -> typing.AsyncGenerator[dict, None]:
    """
    Get documents for export
    :param doc_types: List of document types to export
    :param date_from: Optional start date for filtering documents
    :param date_to: Optional end date for filtering documents
    :return: Generator of documents
    """
    date_from = date_from or dt.datetime.now() - dt.timedelta(days=CONFIG.EXPORT_DEFAULT_AGE_IN_DAYS)
    date_to = date_to or dt.datetime.now()

    doc_query = ("SELECT * FROM c "
                 "WHERE c._type = 'doc' "
                 "AND ARRAY_CONTAINS(@doc_types, c.type.key) "
                 "AND @date_from <= c.version.created AND c.version.created < @date_to")
    doc_params = [
        {"name": "@doc_types", "value": doc_types},
        {"name": "@date_from", "value": date_from.isoformat()},
        {"name": "@date_to", "value": date_to.isoformat()},
    ]

    async for doc in c_document.query_items(doc_query, parameters=doc_params, continuation_token_limit=1):
        sheets = await asyncio.gather(*[
            c_document.read_item(sheet["id"], partition_key=doc["subject_id"]) for sheet in doc["sheets"]
        ])
        doc["sheets"] = sheets
        yield doc
