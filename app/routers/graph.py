"""
Microsoft Graph API routes for email and calendar operations.
These routes demonstrate how to use the GraphClient with authenticated users.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.graph_utils import get_graph_client, ensure_valid_token
from app.graph_client import EmailImportance, GraphAPIError, TokenExpiredError


router = APIRouter(prefix="/graph", tags=["graph"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DraftEmailRequest(BaseModel):
    """Request to create a draft email"""
    user_id: str
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    importance: EmailImportance = EmailImportance.NORMAL


class SendEmailRequest(BaseModel):
    """Request to send an email"""
    user_id: str
    draft_id: Optional[str] = None
    to: Optional[List[EmailStr]] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    importance: EmailImportance = EmailImportance.NORMAL


class SearchEmailsRequest(BaseModel):
    """Request to search emails"""
    user_id: str
    query: Optional[str] = None
    folder: str = "inbox"
    top: int = 10
    from_date: Optional[datetime] = None


class ReadEmailRequest(BaseModel):
    """Request to read an email"""
    user_id: str
    message_id: str


class ScheduleMeetingRequest(BaseModel):
    """Request to schedule a meeting"""
    user_id: str
    subject: str
    attendees: List[EmailStr]
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    body: Optional[str] = None
    is_online: bool = False
    timezone: str = "UTC"


# ============================================================================
# Email Operations
# ============================================================================

@router.post("/email/draft")
async def create_draft_email(request: DraftEmailRequest):
    """
    Create a draft email.

    This endpoint creates a draft email in the user's mailbox.
    The draft can be edited later or sent immediately using the send endpoint.
    """
    # Check token validity
    if not ensure_valid_token(request.user_id):
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid. Please refresh or re-authenticate."
        )

    # Get Graph client
    client = get_graph_client(request.user_id)
    if not client:
        raise HTTPException(
            status_code=401,
            detail="No valid authentication found for this user"
        )

    try:
        result = client.write_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            importance=request.importance
        )
        return {
            "success": True,
            "draft_id": result.get("id"),
            "subject": result.get("subject")
        }
    except TokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Please refresh the token."
        )
    except GraphAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/send")
async def send_email(request: SendEmailRequest):
    """
    Send an email.

    Can either send an existing draft (provide draft_id) or
    create and send a new email (provide to, subject, body).
    """
    if not ensure_valid_token(request.user_id):
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid. Please refresh or re-authenticate."
        )

    client = get_graph_client(request.user_id)
    if not client:
        raise HTTPException(
            status_code=401,
            detail="No valid authentication found for this user"
        )

    try:
        client.send_email(
            draft_id=request.draft_id,
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            importance=request.importance
        )
        return {"success": True, "message": "Email sent successfully"}
    except TokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Please refresh the token."
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GraphAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/search")
async def search_emails(request: SearchEmailsRequest):
    """
    Search for emails in user's mailbox.

    Supports KQL (Keyword Query Language) syntax for advanced queries.
    Examples:
    - "from:boss@company.com"
    - "hasAttachments:true"
    - "isRead:false"
    """
    if not ensure_valid_token(request.user_id):
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid. Please refresh or re-authenticate."
        )

    client = get_graph_client(request.user_id)
    if not client:
        raise HTTPException(
            status_code=401,
            detail="No valid authentication found for this user"
        )

    try:
        results = client.search_emails(
            query=request.query,
            folder=request.folder,
            top=request.top,
            from_date=request.from_date
        )
        return {
            "success": True,
            "count": len(results),
            "emails": results
        }
    except TokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Please refresh the token."
        )
    except GraphAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/email/read")
async def read_email(request: ReadEmailRequest):
    """
    Read full email content by message ID.
    """
    if not ensure_valid_token(request.user_id):
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid. Please refresh or re-authenticate."
        )

    client = get_graph_client(request.user_id)
    if not client:
        raise HTTPException(
            status_code=401,
            detail="No valid authentication found for this user"
        )

    try:
        email = client.read_email(request.message_id)
        return {
            "success": True,
            "email": email
        }
    except TokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Please refresh the token."
        )
    except GraphAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Calendar Operations
# ============================================================================

@router.post("/calendar/meeting")
async def schedule_meeting(request: ScheduleMeetingRequest):
    """
    Schedule a calendar meeting.

    Creates a calendar event with the specified attendees.
    Set is_online=true to automatically create a Teams meeting link.
    """
    if not ensure_valid_token(request.user_id):
        raise HTTPException(
            status_code=401,
            detail="Token expired or invalid. Please refresh or re-authenticate."
        )

    client = get_graph_client(request.user_id)
    if not client:
        raise HTTPException(
            status_code=401,
            detail="No valid authentication found for this user"
        )

    try:
        meeting = client.schedule_meeting(
            subject=request.subject,
            attendees=request.attendees,
            start_time=request.start_time,
            end_time=request.end_time,
            location=request.location,
            body=request.body,
            is_online=request.is_online,
            timezone=request.timezone
        )
        return {
            "success": True,
            "meeting_id": meeting.get("id"),
            "subject": meeting.get("subject"),
            "online_meeting_url": meeting.get("onlineMeeting", {}).get("joinUrl")
        }
    except TokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired. Please refresh the token."
        )
    except GraphAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
