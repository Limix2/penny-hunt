from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Boolean, DateTime,
                        ForeignKey, Text, JSON)
from sqlalchemy.orm import relationship
from app.db.session import Base


class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    chain = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String)
    city = Column(String)
    state = Column(String, index=True)
    zip = Column(String, index=True)
    lat = Column(Float)
    lon = Column(Float)
    store_code = Column(String, unique=True, index=True)
    store_cookie = Column(String, nullable=True)
    phone = Column(String)
    hours_json = Column(JSON)
    reliability = Column(Float, default=0.8)
    behavior_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    upc = Column(String, unique=True, index=True)
    sku = Column(String, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    category = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class StoreItem(Base):
    __tablename__ = "store_items"
    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True, nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), index=True, nullable=False)
    current_price = Column(Float)
    regular_price = Column(Float)
    clearance_flag = Column(Boolean, default=False)
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)
    store = relationship("Store")
    item = relationship("Item")


class PriceHistory(Base):
    __tablename__ = "price_history"
    id = Column(Integer, primary_key=True)
    store_item_id = Column(Integer, ForeignKey("store_items.id"), index=True, nullable=False)
    price = Column(Float, nullable=False)
    observed_at = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String)


class PennySignal(Base):
    __tablename__ = "penny_signals"
    id = Column(Integer, primary_key=True)
    store_item_id = Column(Integer, ForeignKey("store_items.id"), index=True, nullable=False)
    signal_type = Column(String, nullable=False)
    signal_value = Column(Float)
    details_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class AiScore(Base):
    __tablename__ = "ai_scores"
    id = Column(Integer, primary_key=True)
    store_item_id = Column(Integer, ForeignKey("store_items.id"), index=True, nullable=False)
    score = Column(Float, nullable=False)
    model_version = Column(String)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Watchlist(Base):
    __tablename__ = "watchlists"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), index=True, nullable=False)
    store_item_id = Column(Integer, ForeignKey("store_items.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class StoreCache(Base):
    __tablename__ = "store_cache"
    id = Column(Integer, primary_key=True)
    zip = Column(String, index=True)
    radius_miles = Column(Float)
    payload_json = Column(JSON)
    fetched_at = Column(DateTime, default=datetime.utcnow)


class VisionLog(Base):
    __tablename__ = "vision_logs"
    id = Column(Integer, primary_key=True)
    model = Column(String)
    cost_usd = Column(Float, default=0.0)
    result_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class StoreNote(Base):
    __tablename__ = "store_notes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True, nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
