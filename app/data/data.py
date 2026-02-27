from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv
from fastapi import HTTPException
from loguru import logger

load_dotenv()

logger.add("log/data.log")


@lru_cache(maxsize=1)
def load_csv() -> pd.DataFrame:
    """Load data.

    Raises:
        HTTPException: _description_

    Returns:
        pd.DataFrame: _description_

    """
    try:
        df = pd.DataFrame({
            "id": list(range(1, 3, 1)),
            "text": ["You are sweet", "Food is life"],
        })
        logger.info("Loaded csv")
        return df
    except Exception:
        logger.error("Error loading csv")
        raise HTTPException(status_code=500, detail="Error loading data")


def get_sdata_summary() -> dict:
    """Get summary statistics about the data.

    Returns:
        dict: _description_

    """
    df = load_csv()
    return {
        "total_records": len(df),
        "columns": list(df.columns),
        "data_types": df.dtypes.to_dict(),
    }
