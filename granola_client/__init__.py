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
    # Add other important Pydantic models you want to be easily accessible
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
    "__version__",
]

# Configure basic logging if the library user hasn't
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())
