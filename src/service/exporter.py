import os
import json
import time
import logging
import datetime as dt

from src.core.config import CONFIG, Export
from src.core.exception import HTTPException
from src.db.cosmos import get_export_data


logger = logging.getLogger(__name__)


async def generate_export(export: Export, date_from: dt.datetime = None, date_to: dt.datetime = None) -> bool:
    """
    Generate (dummy) export
    :param export: Export object containing export configuration
    :param date_from: Date from which to export data
    :param date_to: Date to which to export data
    :return: True if export was generated successfully, raise HTTPException otherwise
    """
    try:
        logger.info(f"started '{export.name}' export")

        export_dir = os.path.join(CONFIG.EXPORT_DIR, export.name)
        count = 0

        os.makedirs(export_dir, exist_ok=True)
        export_file = os.path.join(export_dir, f"{export.name}_{int(time.time() * 100)}.json")

        with open(export_file, "w") as f:
            async for doc in get_export_data(export.doc_types, date_from, date_to):
                f.write(json.dumps(doc))
                f.write("\n")
                count += 1

        logger.info(f"finished '{export.name}' export | exported {count} documents to '{export_file}'")
        return True

    except Exception as e:
        raise HTTPException(
            status_code=500,
            logger_name=__name__,
            logger_lvl=logging.ERROR,
            logger_msg=f"failed to generate export: {str(e)}",
        )

