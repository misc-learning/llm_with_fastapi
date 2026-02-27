from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Login request model.

    Args:
        BaseModel (_type_): _description_

    """

    username: str
    password: str


class QueryRequest(BaseModel):
    """Query request mode.

    Args:
        BaseModel (_type_): _description_

    """

    question: str
    context_length: int | None = 2


class QueryResponse(BaseModel):
    """Query response model.

    Args:
        BaseModel (_type_): _description_

    """

    question: str
    answer: str
    cached: bool
    response_time: float
    user: str


class HealthResponse(BaseModel):
    """Health check response.

    Args:
        BaseModel (_type_): _description_

    """

    status: str
    query_engine_initialized: bool
    cached_queries: int


class DashboardResponse(BaseModel):
    """Dashbaord metrics response.

    Args:
        BaseModel (_type_): _description_

    """

    status: str
    user: str
    role: str
    total_queries: int
    total_users: int
    cached_queries: int
    avg_response_time: float


class TokenResponse(BaseModel):
    """Token response model.

    Args:
        BaseModel (_type_): _description_

    """

    access_token: str
    token_type: str
    role: str


class HistoryResponse(BaseModel):
    """Query history response.

    Args:
        BaseModel (_type_): _description_

    """

    user: str
    query_count: int
    history: list[dict]
