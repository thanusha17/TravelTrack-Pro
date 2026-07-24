from datetime import datetime
from typing import Generic, TypeVar, Optional, List
from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId

# Response wrapper generics for frontend standard shape
T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]):
    data: T
    error: None = None

class ErrorDetail(BaseModel):
    code: str
    message: str

class ErrorResponse(BaseModel):
    data: None = None
    error: ErrorDetail

# Authentication Schemas
class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    home_currency: Optional[str] = "INR"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: PydanticObjectId
    name: str
    email: EmailStr
    home_currency: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# Journey Schemas
class JourneyCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    destinations: List[str] = []
    currencies: List[str] = []
    total_budget: float = Field(..., gt=0)
    start_date: datetime
    end_date: datetime

class JourneyOut(BaseModel):
    id: PydanticObjectId
    title: str
    owner_id: PydanticObjectId
    member_ids: List[PydanticObjectId] = []
    destinations: List[str] = []
    currencies: List[str] = []
    total_budget: float
    start_date: datetime
    end_date: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Expense Schemas
class ExpenseSplitOut(BaseModel):
    user_id: PydanticObjectId
    share_amount: float
    has_settled: bool = False

    class Config:
        from_attributes = True

class ExpenseSplitCreate(BaseModel):
    user_id: PydanticObjectId
    share_amount: float

class ExpenseCreate(BaseModel):
    journey_id: PydanticObjectId
    amount_local: float = Field(..., gt=0)
    currency_local: str = Field(..., min_length=3, max_length=3)
    category: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    created_at: Optional[datetime] = None
    splits: Optional[List[ExpenseSplitCreate]] = None

class ExpenseOut(BaseModel):
    id: PydanticObjectId
    journey_id: PydanticObjectId
    paid_by: PydanticObjectId
    amount_local: float
    currency_local: str
    amount_home: float
    exchange_rate_used: float
    category: str
    description: str
    splits: List[ExpenseSplitOut] = []
    receipt_url: Optional[str] = None
    vat_eligible: bool
    is_scam_flag: bool
    scam_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# LLM Parser Schemas
class ExpenseParseTextRequest(BaseModel):
    text: str

class ExpenseParseResponse(BaseModel):
    amount_local: float
    currency_local: str
    category: str
    description: str
    created_at: Optional[datetime] = None

class ExpenseUpdate(BaseModel):
    amount_local: Optional[float] = Field(None, gt=0)
    currency_local: Optional[str] = Field(None, min_length=3, max_length=3)
    category: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    created_at: Optional[datetime] = None

class BudgetPacingResponse(BaseModel):
    status: str
    projected_exhaustion_date: str
    advisory_message: str
    days_elapsed: int
    days_remaining: int
    amount_spent: float
    amount_remaining: float

class SettlementOut(BaseModel):
    from_user_id: str
    from_user_name: str
    to_user_id: str
    to_user_name: str
    amount: float

class MemberBalanceOut(BaseModel):
    user_id: str
    user_name: str
    net_balance: float

class SettleResponse(BaseModel):
    balances: List[MemberBalanceOut]
    settlements: List[SettlementOut]

class MemberAddRequest(BaseModel):
    name: str


class ScamChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str


class ScamChatRequest(BaseModel):
    message: str
    history: List[ScamChatMessage] = []


class ScamChatResponse(BaseModel):
    reply: str





