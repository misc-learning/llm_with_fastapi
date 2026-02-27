from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

from dotenv import load_dotenv
from loguru import logger

load_dotenv()

logger.add("log/analytics.log")

request_history: Dict[str, List[Dict]] = defaultdict(list)
query_cache: Dict[str, Dict] = {}


def track_request(username: str, question: str, response_time: float):
    """Track user request for analytics

    Args:
        username (str): _description_
        question (str): _description_
        response_time (float): _description_
    """
    request_history[username].append(
        {
            "question": question,
            "timestamp": datetime.now(timezone.utc),
            "response_time": response_time,
        }
    )
    logger.info(f"Request tracked for {username}")


def cache_query(cache_key: str, anwer: str, username: str):
    """Cache query result

    Args:
        cahce_key (str): _description_
        anwer (str): _description_
        username (str): _description_
    """
    query_cache[cache_key] = {
        "answer": anwer,
        "timestamp": datetime.now(timezone.utc),
        "user": username,
    }
    logger.info(f"Query cached with key: {cache_key[:30]}...")


def get_cached_query(cache_key: str) -> dict:
    """Get cached query result

    Args:
        cache_key (str): _description_

    Returns:
        dict: _description_
    """
    return query_cache.get(cache_key)  # type: ignore


def get_user_history(username: str) -> List[Dict]:
    """Get query history for user

    Args:
        username (str): _description_

    Returns:
        List[Dict]: _description_
    """
    return request_history.get(username, [])


def get_analytics_summary() -> dict:
    """Get comprehensive analytics summary

    Returns:
        dict: _description_
    """
    total_queries = sum(len(queries) for queries in request_history.values())
    total_users = len(request_history)
    avg_response_time = 0
    all_times = []
    for queries in request_history.values():
        all_times.extend([q.get("responset_time", 0) for q in queries])
    if all_times:
        avg_response_time = sum(all_times) / len(all_times)

    return {
        "total_queries": total_queries,
        "total_users": total_users,
        "cached_queries": len(query_cache),
        "avg_response_time": round(avg_response_time, 3),
        "cache_size": sum(len(str(v)) for v in query_cache.values()),
    }


def clear_old_cache(max_age_seconds: int = 3000):
    """Clear cache entries older than max age

    Args:
        max_age_seconds (int, optional): _description_. Defaults to 3000.
    """
    now = datetime.now(timezone.utc)
    keys_to_remove = []

    for key, value in query_cache.items():
        age = (now - value["timestamp"]).total_seconds()
        if age > max_age_seconds:
            keys_to_remove.append(key)
        for key in keys_to_remove:
            del query_cache[key]

    logger.info(f"Cleared {len(keys_to_remove)} old cache entries")
