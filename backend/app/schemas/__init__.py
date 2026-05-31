from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

_orm = ConfigDict(from_attributes=True)


class StoreOut(BaseModel):
    model_config = _orm
    id: int
    chain: str
    name: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    phone: Optional[str] = None
    hours_json: Optional[dict] = None
    reliability: Optional[float] = None
    behavior_score: Optional[float] = None
    store_cookie: Optional[str] = None


class ItemOut(BaseModel):
    model_config = _orm
    id: int
    name: str
    upc: Optional[str] = None
    sku: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    image_url: Optional[str] = None


class Candidate(BaseModel):
    id: int
    store: StoreOut
    item: ItemOut
    current_price: Optional[float] = None
    regular_price: Optional[float] = None
    clearance_flag: bool = False
    last_seen_at: Optional[datetime] = None
    score: Optional[float] = None
    model_version: Optional[str] = None
    explanation: Optional[str] = None
    scored_at: Optional[datetime] = None


class PricePoint(BaseModel):
    model_config = _orm
    price: float
    observed_at: datetime
    source: Optional[str] = None


class ScorePoint(BaseModel):
    model_config = _orm
    score: float
    model_version: Optional[str] = None
    explanation: Optional[str] = None
    created_at: datetime


class ItemDetail(Candidate):
    price_history: list[PricePoint] = []
    score_history: list[ScorePoint] = []


class StoreSummary(StoreOut):
    high_score_count: int = 0
    open_now: bool = False
    distance_miles: Optional[float] = None
    eta_min: Optional[int] = None


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WatchlistIn(BaseModel):
    name: str


class WatchlistOut(BaseModel):
    model_config = _orm
    id: int
    name: str


class NoteIn(BaseModel):
    text: str


class NoteOut(BaseModel):
    model_config = _orm
    id: int
    text: str
    created_at: datetime


class VisionResult(BaseModel):
    model: str
    product_guess: str
    penny_likelihood: float
    clearance_likelihood: float
    confidence: float
    explanation: str
    cost_usd: float
    daily_spent_usd: float
