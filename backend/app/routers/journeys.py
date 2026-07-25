from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from beanie import PydanticObjectId

from datetime import datetime
from app.models import Journey, User, Expense
from app.schemas import (
    SuccessResponse, JourneyCreate, JourneyOut, BudgetPacingResponse, 
    SettleResponse, SettlementOut, MemberBalanceOut, MemberAddRequest, UserOut,
    ScamChatRequest, ScamChatResponse
)
from app.utils.auth_deps import get_current_user
from app.utils.llm import generate_budget_pacing, generate_scam_chat_response

router = APIRouter(prefix="/api/journeys", tags=["Journeys"])

@router.post("", response_model=SuccessResponse[JourneyOut], status_code=status.HTTP_201_CREATED)
async def create_journey(
    journey_data: JourneyCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new journey and sets the current user as the owner and primary member.
    """
    journey = Journey(
        title=journey_data.title,
        owner_id=current_user.id,
        member_ids=[current_user.id],
        destinations=journey_data.destinations,
        currencies=journey_data.currencies,
        total_budget=journey_data.total_budget,
        start_date=journey_data.start_date,
        end_date=journey_data.end_date,
        is_active=True
    )
    await journey.insert()
    
    return SuccessResponse(data=journey)

@router.get("", response_model=SuccessResponse[List[JourneyOut]])
async def list_journeys(
    current_user: User = Depends(get_current_user)
):
    """
    List all journeys owned by or associated with the current user.
    """
    from beanie.operators import Or
    # Find journeys where owner_id is current user OR user is in member_ids
    journeys = await Journey.find(
        Or(Journey.owner_id == current_user.id, Journey.member_ids == current_user.id)
    ).to_list()
    
    return SuccessResponse(data=journeys)

@router.get("/{id}", response_model=SuccessResponse[JourneyOut])
async def get_journey(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Fetch a single journey by ID if the user is authorized.
    """
    try:
        oid = PydanticObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ID",
                "message": f"'{id}' is not a valid journey ID format."
            }
        )

    journey = await Journey.get(oid)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOURNEY_NOT_FOUND",
                "message": f"The journey with ID {id} does not exist in the database."
            }
        )
        
    # Check if the user is owner or member of this journey
    if journey.owner_id != current_user.id and current_user.id not in journey.member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "You do not have permission to view this journey."
            }
        )
        
    return SuccessResponse(data=journey)

@router.get("/{id}/pace", response_model=SuccessResponse[BudgetPacingResponse])
async def get_journey_pace(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the budget pacing status for a specific journey.
    Calculates elapsed/remaining days and total spent programmatically,
    then requests status and advisory messages from Gemini.
    """
    try:
        oid = PydanticObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ID",
                "message": f"'{id}' is not a valid journey ID format."
            }
        )

    journey = await Journey.get(oid)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOURNEY_NOT_FOUND",
                "message": f"The journey with ID {id} does not exist in the database."
            }
        )

    # Check authorization
    if journey.owner_id != current_user.id and current_user.id not in journey.member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "You do not have permission to view pacing details for this journey."
            }
        )

    # Pull the journey's full expense list
    expenses = await Expense.find(Expense.journey_id == oid).to_list()

    # Calculate days elapsed, days remaining, amount spent, amount remaining
    start_date = journey.start_date.date()
    end_date = journey.end_date.date()
    
    # Use current UTC date context
    today = datetime.utcnow().date()

    # Total days in journey (inclusive of start and end dates)
    total_days = max(1, (end_date - start_date).days + 1)

    # Calculate days elapsed (inclusive)
    if today < start_date:
        days_elapsed = 0
    elif today > end_date:
        days_elapsed = total_days
    else:
        days_elapsed = (today - start_date).days + 1

    # Days remaining
    days_remaining = max(0, total_days - days_elapsed)

    # Calculate amount spent in home currency
    amount_spent = sum(e.amount_home for e in expenses)
    amount_remaining = journey.total_budget - amount_spent

    today_str = today.strftime("%Y-%m-%d")

    # Generate budget pacing status via LLM with fallback
    pacing_data = generate_budget_pacing(
        total_budget=journey.total_budget,
        days_remaining=days_remaining,
        spend_so_far=amount_spent,
        days_elapsed=days_elapsed,
        today_date=today_str
    )

    response_data = BudgetPacingResponse(
        status=pacing_data.get("status", "under_budget"),
        projected_exhaustion_date=pacing_data.get("projected_exhaustion_date", "Never"),
        advisory_message=pacing_data.get("advisory_message", "No advice available."),
        days_elapsed=days_elapsed,
        days_remaining=days_remaining,
        amount_spent=amount_spent,
        amount_remaining=amount_remaining
    )

    return SuccessResponse(data=response_data)

@router.put("/{id}", response_model=SuccessResponse[JourneyOut])
async def update_journey(
    id: str,
    journey_data: JourneyCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing journey. Restricts access to the trip owner.
    """
    try:
        oid = PydanticObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ID",
                "message": f"'{id}' is not a valid journey ID format."
            }
        )

    journey = await Journey.get(oid)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOURNEY_NOT_FOUND",
                "message": f"The journey with ID {id} does not exist in the database."
            }
        )

    # Check authorization (only owner can edit)
    if journey.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "You do not have permission to update this journey."
            }
        )

    # Update journey properties
    journey.title = journey_data.title
    journey.destinations = journey_data.destinations
    journey.currencies = journey_data.currencies
    journey.total_budget = journey_data.total_budget
    journey.start_date = journey_data.start_date
    journey.end_date = journey_data.end_date

    await journey.save()
    return SuccessResponse(data=journey)

@router.post("/{id}/members", response_model=SuccessResponse[UserOut])
async def add_journey_member(
    id: str,
    payload: MemberAddRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Adds a new member to the journey by name (creates a dummy User account).
    Only journey members or owner can add new members.
    """
    try:
        oid = PydanticObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ID",
                "message": f"'{id}' is not a valid journey ID format."
            }
        )

    journey = await Journey.get(oid)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOURNEY_NOT_FOUND",
                "message": f"The journey with ID {id} does not exist in the database."
            }
        )

    # Authorization check
    if journey.owner_id != current_user.id and current_user.id not in journey.member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "You do not have permission to modify this journey's members."
            }
        )

    import uuid
    # Create a dummy user
    dummy_email = f"{payload.name.lower().replace(' ', '_')}_{id}_{uuid.uuid4().hex[:6]}@dummy.traveltrack"
    dummy_user = User(
        email=dummy_email,
        name=payload.name,
        hashed_password=None,
        home_currency=current_user.home_currency
    )
    await dummy_user.insert()

    # Append to journey
    if dummy_user.id not in journey.member_ids:
        journey.member_ids.append(dummy_user.id)
        await journey.save()

    return SuccessResponse(data=dummy_user)

@router.get("/{id}/settle", response_model=SuccessResponse[SettleResponse])
async def get_journey_settle(
    id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Computes members' net balances (paid - owed) and returns the greedy settlements list.
    """
    try:
        oid = PydanticObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ID",
                "message": f"'{id}' is not a valid journey ID format."
            }
        )

    journey = await Journey.get(oid)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOURNEY_NOT_FOUND",
                "message": f"The journey with ID {id} does not exist in the database."
            }
        )

    # Authorization check
    if journey.owner_id != current_user.id and current_user.id not in journey.member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "You do not have permission to view settlements for this journey."
            }
        )

    # Pull members to map IDs to names
    from beanie.operators import In
    members = await User.find(In(User.id, journey.member_ids)).to_list()
    user_name_map = {m.id: m.name for m in members}

    # Pull the journey's full expense list
    expenses = await Expense.find(Expense.journey_id == oid).to_list()

    # Calculate net balances (paid - owed) in home currency (INR)
    # Initialize all members with 0.0 balance
    balances = {mid: 0.0 for mid in journey.member_ids}

    for exp in expenses:
        # Payer gets credit
        payer_id = exp.paid_by
        if payer_id in balances:
            balances[payer_id] += exp.amount_home

        # Debtors owe share proportional to local currency amount
        for split in exp.splits:
            participant_id = split.user_id
            if participant_id in balances and exp.amount_local > 0:
                owed_share_home = exp.amount_home * (split.share_amount / exp.amount_local)
                balances[participant_id] -= owed_share_home

    # Construct the balances response
    balances_out = [
        MemberBalanceOut(
            user_id=str(mid),
            user_name=user_name_map.get(mid, "Unknown"),
            net_balance=round(bal, 2)
        )
        for mid, bal in balances.items()
    ]

    # Run the greedy matching algorithm
    # Debtors: net_balance < -0.01 (owes money)
    # Creditors: net_balance > 0.01 (owed money)
    debtors = [[mid, abs(bal)] for mid, bal in balances.items() if bal < -0.01]
    creditors = [[mid, bal] for mid, bal in balances.items() if bal > 0.01]

    settlements = []
    # Greedy loop: match largest debtor to largest creditor
    while debtors and creditors:
        # Sort so index 0 has the largest absolute balance
        debtors.sort(key=lambda x: x[1], reverse=True)
        creditors.sort(key=lambda x: x[1], reverse=True)

        d = debtors[0]
        c = creditors[0]

        settle_amt = min(d[1], c[1])
        if settle_amt > 0.01:
            settlements.append(
                SettlementOut(
                    from_user_id=str(d[0]),
                    from_user_name=user_name_map.get(d[0], "Unknown"),
                    to_user_id=str(c[0]),
                    to_user_name=user_name_map.get(c[0], "Unknown"),
                    amount=round(settle_amt, 2)
                )
            )

        d[1] -= settle_amt
        c[1] -= settle_amt

        # Remove from active lists if fully settled
        if d[1] <= 0.01:
            debtors.pop(0)
        if c[1] <= 0.01:
            creditors.pop(0)

    response_data = SettleResponse(
        balances=balances_out,
        settlements=settlements
    )

    return SuccessResponse(data=response_data)


@router.post("/{id}/scam-chat", response_model=SuccessResponse[ScamChatResponse])
async def post_journey_scam_chat(
    id: str,
    payload: ScamChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Interacts with the AI Scam Consultant for the given journey.
    Provides real-time conversation and verification of prices contextually.
    """
    try:
        oid = PydanticObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_ID",
                "message": f"'{id}' is not a valid journey ID format."
            }
        )

    journey = await Journey.get(oid)
    if not journey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOURNEY_NOT_FOUND",
                "message": f"The journey with ID {id} does not exist in the database."
            }
        )

    # Authorization check
    if journey.owner_id != current_user.id and current_user.id not in journey.member_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "You do not have permission to access this journey."
            }
        )

    # Call AI chat service
    reply = generate_scam_chat_response(
        message=payload.message,
        history=payload.history,
        destinations=journey.destinations,
        home_currency=current_user.home_currency
    )

    return SuccessResponse(data=ScamChatResponse(reply=reply))

