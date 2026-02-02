# granola_client/__init__.py
__version__ = "0.3.0"

from .client import GranolaClient
from .errors import (
    GranolaAPIError, GranolaAuthError, GranolaRateLimitError,
    GranolaTimeoutError, GranolaValidationError
)
from .types import (
    # Client/HTTP Options
    ClientOpts, HttpOpts,
    # Core Models
    Document, DocumentsResponse,
    DocumentMetadata, TranscriptSegment, PanelTemplate,
    # Entity Models
    Person,
    # Feature/Integration Models
    FeatureFlagsResponse,
    # Subscription Models
    SubscriptionsResponse,
    # Payload Models
    UpdateDocumentPayload, UpdateDocumentPanelPayload,
    # Filter Models
    GetDocumentsFilters,
    # New models from API discovery
    UserInfo,
    Workspace, WorkspacesResponse, WorkspaceMember, WorkspaceMembersResponse,
    CalendarEvent, CalendarEventsResponse,
    CreateDocumentPayload, CreateDocumentResponse,
    DeleteDocumentPayload,
    ShareDocumentPayload, UnshareDocumentPayload,
    DocumentAccessUser, DocumentAccessResponse,
    CreateFolderPayload, CreateFolderResponse, UpdateFolderPayload,
    AddDocumentToFolderPayload, RemoveDocumentFromFolderPayload,
    SearchQuery, SearchResult, SearchResponse,
    SaveToNotionPayload, SaveToNotionResponse,
    SlackIntegrationResponse, PostSlackMessagePayload, SlackChannel, SlackChannelsResponse,
)
from .pagination import PaginatedResponse # This is also a Pydantic model now

# For easier imports like: from granola_client import GranolaClient
__all__ = [
    "GranolaClient",
    "GranolaAPIError",
    "GranolaAuthError",
    "GranolaRateLimitError",
    "GranolaTimeoutError",
    "GranolaValidationError",
    # Options
    "ClientOpts", "HttpOpts",
    # Models
    "Document", "DocumentsResponse",
    "DocumentMetadata", "TranscriptSegment", "PanelTemplate", "Person",
    "FeatureFlagsResponse", "SubscriptionsResponse",
    "UpdateDocumentPayload", "UpdateDocumentPanelPayload", "GetDocumentsFilters",
    "PaginatedResponse",
    # New exports from API discovery
    "UserInfo",
    "Workspace", "WorkspacesResponse", "WorkspaceMember", "WorkspaceMembersResponse",
    "CalendarEvent", "CalendarEventsResponse",
    "CreateDocumentPayload", "CreateDocumentResponse",
    "DeleteDocumentPayload",
    "ShareDocumentPayload", "UnshareDocumentPayload",
    "DocumentAccessUser", "DocumentAccessResponse",
    "CreateFolderPayload", "CreateFolderResponse", "UpdateFolderPayload",
    "AddDocumentToFolderPayload", "RemoveDocumentFromFolderPayload",
    "SearchQuery", "SearchResult", "SearchResponse",
    "SaveToNotionPayload", "SaveToNotionResponse",
    "SlackIntegrationResponse", "PostSlackMessagePayload", "SlackChannel", "SlackChannelsResponse",
    "__version__",
]

# Configure basic logging if the library user hasn't
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
