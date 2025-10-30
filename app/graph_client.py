"""
Microsoft Graph API client wrapper for Outlook operations.
Provides methods for email and calendar operations with error handling and retries.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import time
import httpx
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailImportance(str, Enum):
    """Email importance levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class GraphAPIError(Exception):
    """Base exception for Graph API errors"""
    pass


class TokenExpiredError(GraphAPIError):
    """Raised when access token is expired"""
    pass


class RateLimitError(GraphAPIError):
    """Raised when rate limit is exceeded"""
    pass


class GraphClient:
    """
    Wrapper for Microsoft Graph API operations.
    Handles authentication, retries, and error handling.
    """

    BASE_URL = "https://graph.microsoft.com/v1.0"
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1  # seconds

    def __init__(self, access_token: str):
        """
        Initialize Graph API client with access token.

        Args:
            access_token: Valid Microsoft Graph API access token
        """
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Graph API with exponential backoff retry logic.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            retry_count: Current retry attempt number

        Returns:
            JSON response from API

        Raises:
            TokenExpiredError: If access token is expired
            RateLimitError: If rate limit is exceeded
            GraphAPIError: For other API errors
        """
        url = f"{self.BASE_URL}{endpoint}"

        # Log request
        logger.info(f"Making {method} request to {endpoint}")
        if data:
            logger.debug(f"Request data: {data}")
        if params:
            logger.debug(f"Query params: {params}")

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params
                )

            # Log response
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")

            # Handle different status codes
            if response.status_code == 401:
                raise TokenExpiredError("Access token expired or invalid")

            if response.status_code == 429:
                # Rate limit exceeded
                retry_after = int(response.headers.get("Retry-After", 60))
                raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")

            if response.status_code >= 500:
                # Server error - retry with exponential backoff
                if retry_count < self.MAX_RETRIES:
                    delay = self.INITIAL_RETRY_DELAY * (2 ** retry_count)
                    logger.warning(f"Server error {response.status_code}, retrying in {delay}s (attempt {retry_count + 1}/{self.MAX_RETRIES})")
                    time.sleep(delay)
                    return self._make_request(method, endpoint, data, params, retry_count + 1)
                else:
                    raise GraphAPIError(f"Server error after {self.MAX_RETRIES} retries: {response.text}")

            if response.status_code >= 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", error_msg)
                except:
                    pass
                raise GraphAPIError(f"API error {response.status_code}: {error_msg}")

            # Success - return JSON response
            if response.status_code == 204:
                return {}
            return response.json()

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            # Network error - retry with exponential backoff
            if retry_count < self.MAX_RETRIES:
                delay = self.INITIAL_RETRY_DELAY * (2 ** retry_count)
                logger.warning(f"Network error, retrying in {delay}s (attempt {retry_count + 1}/{self.MAX_RETRIES}): {e}")
                time.sleep(delay)
                return self._make_request(method, endpoint, data, params, retry_count + 1)
            else:
                raise GraphAPIError(f"Network error after {self.MAX_RETRIES} retries: {str(e)}")

    # ============================================================================
    # EMAIL OPERATIONS
    # ============================================================================

    def write_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        importance: EmailImportance = EmailImportance.NORMAL,
        body_type: str = "HTML"
    ) -> Dict[str, Any]:
        """
        Create a draft email in the user's mailbox.

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body content
            cc: Optional list of CC recipient email addresses
            importance: Email importance level (low, normal, high)
            body_type: Body content type ("Text" or "HTML")

        Returns:
            Draft email object with id, subject, etc.

        Example:
            >>> draft = client.write_email(
            ...     to=["user@example.com"],
            ...     subject="Meeting Follow-up",
            ...     body="<p>Thanks for the meeting!</p>",
            ...     importance=EmailImportance.HIGH
            ... )
            >>> print(draft["id"])
        """
        # Build email message
        message = {
            "subject": subject,
            "importance": importance.value,
            "body": {
                "contentType": body_type,
                "content": body
            },
            "toRecipients": [
                {"emailAddress": {"address": addr}} for addr in to
            ]
        }

        if cc:
            message["ccRecipients"] = [
                {"emailAddress": {"address": addr}} for addr in cc
            ]

        # Create draft
        endpoint = "/me/messages"
        result = self._make_request("POST", endpoint, data=message)

        logger.info(f"Created draft email: {result.get('id')}")
        return result

    def send_email(
        self,
        draft_id: Optional[str] = None,
        to: Optional[List[str]] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        importance: EmailImportance = EmailImportance.NORMAL,
        body_type: str = "HTML"
    ) -> None:
        """
        Send an email. Can send an existing draft or create and send a new email.

        Args:
            draft_id: ID of existing draft to send (if provided, other params ignored)
            to: List of recipient email addresses (required if draft_id not provided)
            subject: Email subject (required if draft_id not provided)
            body: Email body content (required if draft_id not provided)
            cc: Optional list of CC recipient email addresses
            importance: Email importance level
            body_type: Body content type ("Text" or "HTML")

        Example:
            >>> # Send existing draft
            >>> client.send_email(draft_id="AAMkAG...")
            >>>
            >>> # Create and send new email
            >>> client.send_email(
            ...     to=["user@example.com"],
            ...     subject="Quick message",
            ...     body="Hello!"
            ... )
        """
        if draft_id:
            # Send existing draft
            endpoint = f"/me/messages/{draft_id}/send"
            self._make_request("POST", endpoint)
            logger.info(f"Sent draft email: {draft_id}")
        else:
            # Create and send new email
            if not to or not subject or not body:
                raise ValueError("to, subject, and body are required when draft_id is not provided")

            # Build email message
            message = {
                "subject": subject,
                "importance": importance.value,
                "body": {
                    "contentType": body_type,
                    "content": body
                },
                "toRecipients": [
                    {"emailAddress": {"address": addr}} for addr in to
                ]
            }

            if cc:
                message["ccRecipients"] = [
                    {"emailAddress": {"address": addr}} for addr in cc
                ]

            endpoint = "/me/sendMail"
            self._make_request("POST", endpoint, data={"message": message})
            logger.info(f"Sent new email to {to}")

    def search_emails(
        self,
        query: Optional[str] = None,
        folder: str = "inbox",
        top: int = 10,
        from_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for emails in user's mailbox.

        Args:
            query: Search query using KQL (Keyword Query Language) syntax
                   Examples: "from:user@example.com", "hasAttachments:true", "budget report"
            folder: Folder to search in (inbox, sentitems, drafts, etc.)
            top: Maximum number of results to return (default 10, max 1000)
            from_date: Only return emails received after this date

        Returns:
            List of email objects

        Example:
            >>> # Search for unread emails from specific sender
            >>> emails = client.search_emails(
            ...     query="from:boss@company.com isRead:false",
            ...     folder="inbox",
            ...     top=5
            ... )
        """
        # Build endpoint
        endpoint = f"/me/mailFolders/{folder}/messages"

        # Build query parameters
        params = {
            "$top": min(top, 1000),  # Cap at 1000
            "$orderby": "receivedDateTime DESC"
        }

        # Build filter string
        filters = []
        if from_date:
            date_str = from_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            filters.append(f"receivedDateTime ge {date_str}")

        if filters:
            params["$filter"] = " and ".join(filters)

        if query:
            params["$search"] = f'"{query}"'

        # Make request
        result = self._make_request("GET", endpoint, params=params)
        messages = result.get("value", [])

        logger.info(f"Found {len(messages)} emails matching query")
        return messages

    def read_email(self, message_id: str) -> Dict[str, Any]:
        """
        Retrieve full email content by message ID.

        Args:
            message_id: ID of the email message

        Returns:
            Email object with full details

        Example:
            >>> email = client.read_email("AAMkAGI...")
            >>> print(email["subject"])
            >>> print(email["body"]["content"])
        """
        endpoint = f"/me/messages/{message_id}"

        result = self._make_request("GET", endpoint)
        logger.info(f"Retrieved email: {message_id}")

        return result

    # ============================================================================
    # CALENDAR OPERATIONS
    # ============================================================================

    def check_scheduling_assistant(
        self,
        attendees: List[str],
        duration: int,
        start_date: datetime,
        end_date: datetime,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Find available meeting times using the Scheduling Assistant.

        Args:
            attendees: List of attendee email addresses
            duration: Meeting duration in minutes
            start_date: Start of time window to search
            end_date: End of time window to search
            timezone: Timezone for the search (default UTC)

        Returns:
            Schedule information including available time slots

        Example:
            >>> availability = client.check_scheduling_assistant(
            ...     attendees=["alice@company.com", "bob@company.com"],
            ...     duration=60,
            ...     start_date=datetime.now(),
            ...     end_date=datetime.now() + timedelta(days=7),
            ...     timezone="Eastern Standard Time"
            ... )
        """
        endpoint = "/me/calendar/getSchedule"

        # Format dates for API
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S")

        data = {
            "schedules": attendees,
            "startTime": {
                "dateTime": start_str,
                "timeZone": timezone
            },
            "endTime": {
                "dateTime": end_str,
                "timeZone": timezone
            },
            "availabilityViewInterval": duration
        }

        result = self._make_request("POST", endpoint, data=data)
        logger.info(f"Retrieved schedule for {len(attendees)} attendees")

        return result

    def schedule_meeting(
        self,
        subject: str,
        attendees: List[str],
        start_time: datetime,
        end_time: datetime,
        location: Optional[str] = None,
        body: Optional[str] = None,
        is_online: bool = False,
        timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """
        Create a calendar event (meeting).

        Args:
            subject: Meeting subject/title
            attendees: List of attendee email addresses
            start_time: Meeting start time
            end_time: Meeting end time
            location: Optional meeting location
            body: Optional meeting description
            is_online: Whether to create an online meeting (Teams link)
            timezone: Timezone for the meeting

        Returns:
            Created event object

        Example:
            >>> meeting = client.schedule_meeting(
            ...     subject="Project Review",
            ...     attendees=["team@company.com"],
            ...     start_time=datetime(2024, 1, 15, 14, 0),
            ...     end_time=datetime(2024, 1, 15, 15, 0),
            ...     location="Conference Room A",
            ...     body="Quarterly project review meeting",
            ...     is_online=True
            ... )
        """
        # Build event object
        event = {
            "subject": subject,
            "start": {
                "dateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": timezone
            },
            "end": {
                "dateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "timeZone": timezone
            },
            "attendees": [
                {
                    "emailAddress": {"address": addr},
                    "type": "required"
                }
                for addr in attendees
            ]
        }

        if location:
            event["location"] = {"displayName": location}

        if body:
            event["body"] = {
                "contentType": "HTML",
                "content": body
            }

        if is_online:
            event["isOnlineMeeting"] = True
            event["onlineMeetingProvider"] = "teamsForBusiness"

        endpoint = "/me/events"
        result = self._make_request("POST", endpoint, data=event)

        logger.info(f"Created meeting: {result.get('id')} - {subject}")
        return result
