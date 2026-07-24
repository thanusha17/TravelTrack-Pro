from datetime import datetime
from typing import List, Optional
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field

class User(Document):
    email: str
    name: str
    hashed_password: Optional[str] = None
    home_currency: str = "INR"
    card_forex_fee_pct: float = 3.5
    atm_fee_flat: float = 250.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"

class Journey(Document):
    title: str
    owner_id: PydanticObjectId
    member_ids: List[PydanticObjectId] = []
    destinations: List[str] = []   # e.g., ['Bangkok', 'Tokyo']
    currencies: List[str] = []     # e.g., ['THB', 'JPY']
    total_budget: float
    start_date: datetime
    end_date: datetime
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "journeys"

class ExpenseSplit(BaseModel):
    user_id: PydanticObjectId
    share_amount: float
    has_settled: bool = False

class Expense(Document):
    journey_id: PydanticObjectId
    paid_by: PydanticObjectId
    amount_local: float
    currency_local: str
    amount_home: float
    exchange_rate_used: float
    category: str             # Food, Stay, Transport, Shopping, Activities, Misc
    description: str
    splits: List[ExpenseSplit] = []
    receipt_url: Optional[str] = None
    vat_eligible: bool = False
    is_scam_flag: bool = False
    scam_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "expenses"

