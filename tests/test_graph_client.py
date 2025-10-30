"""
Unit tests for GraphClient with mocked HTTP requests
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import httpx
from app.graph_client import (
    GraphClient,
    EmailImportance,
    GraphAPIError,
    TokenExpiredError,
    RateLimitError
)


@pytest.fixture
def mock_access_token():
    """Fixture providing a mock access token"""
    return "mock_access_token_12345"


@pytest.fixture
def graph_client(mock_access_token):
    """Fixture providing a GraphClient instance"""
    return GraphClient(mock_access_token)


class TestGraphClientInit:
    """Tests for GraphClient initialization"""

    def test_initialization(self, mock_access_token):
        """Test that client initializes with correct headers"""
        client = GraphClient(mock_access_token)
        assert client.access_token == mock_access_token
        assert client.headers["Authorization"] == f"Bearer {mock_access_token}"
        assert client.headers["Content-Type"] == "application/json"


class TestEmailOperations:
    """Tests for email-related operations"""

    @patch('httpx.Client')
    def test_write_email_success(self, mock_client_class, graph_client):
        """Test creating a draft email"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "AAMkAGI2THVSAAA=",
            "subject": "Test Email",
            "importance": "normal"
        }

        # Setup mock
        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Call method
        result = graph_client.write_email(
            to=["test@example.com"],
            subject="Test Email",
            body="Test body",
            importance=EmailImportance.NORMAL
        )

        # Assertions
        assert result["id"] == "AAMkAGI2THVSAAA="
        assert result["subject"] == "Test Email"
        mock_client.request.assert_called_once()

        # Check request was made correctly
        call_args = mock_client.request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "/me/messages" in call_args.kwargs["url"]
        assert call_args.kwargs["json"]["subject"] == "Test Email"
        assert call_args.kwargs["json"]["toRecipients"][0]["emailAddress"]["address"] == "test@example.com"

    @patch('httpx.Client')
    def test_write_email_with_cc(self, mock_client_class, graph_client):
        """Test creating draft email with CC recipients"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "test_id"}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        graph_client.write_email(
            to=["to@example.com"],
            subject="Test",
            body="Body",
            cc=["cc1@example.com", "cc2@example.com"]
        )

        # Check CC recipients were included
        call_args = mock_client.request.call_args
        cc_recipients = call_args.kwargs["json"]["ccRecipients"]
        assert len(cc_recipients) == 2
        assert cc_recipients[0]["emailAddress"]["address"] == "cc1@example.com"

    @patch('httpx.Client')
    def test_send_email_existing_draft(self, mock_client_class, graph_client):
        """Test sending an existing draft"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        draft_id = "AAMkAGI2THVSAAA="
        graph_client.send_email(draft_id=draft_id)

        # Check request was made correctly
        call_args = mock_client.request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert f"/me/messages/{draft_id}/send" in call_args.kwargs["url"]

    @patch('httpx.Client')
    def test_send_email_new(self, mock_client_class, graph_client):
        """Test creating and sending a new email"""
        mock_response = Mock()
        mock_response.status_code = 202
        mock_response.json.return_value = {}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        graph_client.send_email(
            to=["test@example.com"],
            subject="Test",
            body="Body"
        )

        # Check request was made correctly
        call_args = mock_client.request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "/me/sendMail" in call_args.kwargs["url"]
        assert "message" in call_args.kwargs["json"]

    def test_send_email_validation_error(self, graph_client):
        """Test that send_email raises error when required fields missing"""
        with pytest.raises(ValueError) as exc_info:
            graph_client.send_email(to=["test@example.com"])  # Missing subject and body

        assert "subject" in str(exc_info.value)

    @patch('httpx.Client')
    def test_search_emails(self, mock_client_class, graph_client):
        """Test searching for emails"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {"id": "msg1", "subject": "Email 1"},
                {"id": "msg2", "subject": "Email 2"}
            ]
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = graph_client.search_emails(
            query="budget report",
            folder="inbox",
            top=10
        )

        assert len(result) == 2
        assert result[0]["id"] == "msg1"

        # Check query parameters
        call_args = mock_client.request.call_args
        params = call_args.kwargs["params"]
        assert params["$search"] == '"budget report"'
        assert params["$top"] == 10

    @patch('httpx.Client')
    def test_search_emails_with_date_filter(self, mock_client_class, graph_client):
        """Test searching emails with date filter"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        from_date = datetime(2024, 1, 1)
        graph_client.search_emails(from_date=from_date)

        # Check filter was applied
        call_args = mock_client.request.call_args
        params = call_args.kwargs["params"]
        assert "$filter" in params
        assert "2024-01-01" in params["$filter"]

    @patch('httpx.Client')
    def test_read_email(self, mock_client_class, graph_client):
        """Test reading an email by ID"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "msg123",
            "subject": "Test Email",
            "body": {"content": "Email content"}
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = graph_client.read_email("msg123")

        assert result["id"] == "msg123"
        assert result["subject"] == "Test Email"

        # Check correct endpoint
        call_args = mock_client.request.call_args
        assert "/me/messages/msg123" in call_args.kwargs["url"]


class TestCalendarOperations:
    """Tests for calendar-related operations"""

    @patch('httpx.Client')
    def test_check_scheduling_assistant(self, mock_client_class, graph_client):
        """Test checking availability using scheduling assistant"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {
                    "scheduleId": "user1@example.com",
                    "availabilityView": "000000000000000000000000000000000000"
                }
            ]
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        start = datetime.now()
        end = start + timedelta(days=1)

        result = graph_client.check_scheduling_assistant(
            attendees=["user1@example.com"],
            duration=60,
            start_date=start,
            end_date=end,
            timezone="UTC"
        )

        assert "value" in result

        # Check request structure
        call_args = mock_client.request.call_args
        assert "/me/calendar/getSchedule" in call_args.kwargs["url"]
        request_data = call_args.kwargs["json"]
        assert request_data["schedules"] == ["user1@example.com"]
        assert request_data["availabilityViewInterval"] == 60

    @patch('httpx.Client')
    def test_schedule_meeting_basic(self, mock_client_class, graph_client):
        """Test scheduling a basic meeting"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "event123",
            "subject": "Team Meeting",
            "start": {"dateTime": "2024-01-15T14:00:00", "timeZone": "UTC"}
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        start_time = datetime(2024, 1, 15, 14, 0)
        end_time = datetime(2024, 1, 15, 15, 0)

        result = graph_client.schedule_meeting(
            subject="Team Meeting",
            attendees=["user@example.com"],
            start_time=start_time,
            end_time=end_time
        )

        assert result["id"] == "event123"
        assert result["subject"] == "Team Meeting"

        # Check request structure
        call_args = mock_client.request.call_args
        assert "/me/events" in call_args.kwargs["url"]
        event_data = call_args.kwargs["json"]
        assert event_data["subject"] == "Team Meeting"
        assert len(event_data["attendees"]) == 1

    @patch('httpx.Client')
    def test_schedule_meeting_with_location_and_body(self, mock_client_class, graph_client):
        """Test scheduling meeting with location and description"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "event123"}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        graph_client.schedule_meeting(
            subject="Meeting",
            attendees=["user@example.com"],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            location="Conference Room A",
            body="Meeting agenda here"
        )

        # Check location and body were included
        call_args = mock_client.request.call_args
        event_data = call_args.kwargs["json"]
        assert event_data["location"]["displayName"] == "Conference Room A"
        assert event_data["body"]["content"] == "Meeting agenda here"

    @patch('httpx.Client')
    def test_schedule_online_meeting(self, mock_client_class, graph_client):
        """Test scheduling an online meeting with Teams link"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "event123"}

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        graph_client.schedule_meeting(
            subject="Online Meeting",
            attendees=["user@example.com"],
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            is_online=True
        )

        # Check online meeting settings
        call_args = mock_client.request.call_args
        event_data = call_args.kwargs["json"]
        assert event_data["isOnlineMeeting"] is True
        assert event_data["onlineMeetingProvider"] == "teamsForBusiness"


class TestErrorHandling:
    """Tests for error handling and retries"""

    @patch('httpx.Client')
    def test_token_expired_error(self, mock_client_class, graph_client):
        """Test handling of expired token (401)"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(TokenExpiredError) as exc_info:
            graph_client.read_email("test_id")

        assert "expired" in str(exc_info.value).lower()

    @patch('httpx.Client')
    def test_rate_limit_error(self, mock_client_class, graph_client):
        """Test handling of rate limit (429)"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.text = "Rate limit exceeded"

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(RateLimitError) as exc_info:
            graph_client.read_email("test_id")

        assert "rate limit" in str(exc_info.value).lower()

    @patch('httpx.Client')
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_retry_on_server_error(self, mock_sleep, mock_client_class, graph_client):
        """Test retry logic on server error (500)"""
        # First two attempts fail, third succeeds
        mock_responses = [
            Mock(status_code=500, text="Server error"),
            Mock(status_code=500, text="Server error"),
            Mock(status_code=200)
        ]
        mock_responses[2].json.return_value = {"id": "test_id"}

        mock_client = Mock()
        mock_client.request.side_effect = mock_responses
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = graph_client.read_email("test_id")

        # Should succeed on third attempt
        assert result["id"] == "test_id"
        assert mock_client.request.call_count == 3
        # Should have slept twice (with exponential backoff)
        assert mock_sleep.call_count == 2

    @patch('httpx.Client')
    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_client_class, graph_client):
        """Test that max retries is respected"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(GraphAPIError) as exc_info:
            graph_client.read_email("test_id")

        assert "retries" in str(exc_info.value).lower()
        # Should attempt MAX_RETRIES + 1 times (initial + retries)
        assert mock_client.request.call_count == GraphClient.MAX_RETRIES + 1

    @patch('httpx.Client')
    @patch('time.sleep')
    def test_retry_on_network_error(self, mock_sleep, mock_client_class, graph_client):
        """Test retry logic on network error"""
        # First attempt fails, second succeeds
        mock_client = Mock()
        mock_client.request.side_effect = [
            httpx.TimeoutException("Timeout"),
            Mock(status_code=200, json=lambda: {"id": "test_id"})
        ]
        mock_client_class.return_value.__enter__.return_value = mock_client

        result = graph_client.read_email("test_id")

        assert result["id"] == "test_id"
        assert mock_client.request.call_count == 2

    @patch('httpx.Client')
    def test_client_error_no_retry(self, mock_client_class, graph_client):
        """Test that client errors (4xx except 401/429) don't retry"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.json.return_value = {
            "error": {"message": "Resource not found"}
        }

        mock_client = Mock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        with pytest.raises(GraphAPIError) as exc_info:
            graph_client.read_email("invalid_id")

        # Should not retry on 404
        assert mock_client.request.call_count == 1
        assert "404" in str(exc_info.value)
