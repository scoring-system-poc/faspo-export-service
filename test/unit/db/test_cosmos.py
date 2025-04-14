import pytest


@pytest.mark.asyncio
async def test_get_export_data():
    from src.db.cosmos import get_export_data

    docs = []
    async for doc in get_export_data(["doc_type_1", "doc_type_2"]):
        docs.append(doc)

    assert len(docs) == 1
    assert docs[0]["subject_id"] == "x"
    assert docs[0]["sheets"] == [{"id": "sheet_id"}]
    assert docs[0]["sheets"][0]["id"] == "sheet_id"

