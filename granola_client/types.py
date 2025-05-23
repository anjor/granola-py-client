from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field, HttpUrl

# Client Options
class HttpOpts(BaseModel):
    timeout: Optional[int] = 10000  # milliseconds
    retries: Optional[int] = 3
    app_version: Optional[str] = Field(default="6.4.0", alias="appVersion")
    client_type: Optional[str] = Field(default="electron", alias="clientType") # Consider "python-httpx"
    client_platform: Optional[str] = Field(default=None, alias="clientPlatform") # Will be auto-detected
    client_architecture: Optional[str] = Field(default=None, alias="clientArchitecture") # Will be auto-detected
    electron_version: Optional[str] = Field(default="33.4.5", alias="electronVersion")
    chrome_version: Optional[str] = Field(default="130.0.6723.191", alias="chromeVersion")
    node_version: Optional[str] = Field(default="20.18.3", alias="nodeVersion")
    os_version: Optional[str] = Field(default=None, alias="osVersion") # Will be auto-detected
    os_build: Optional[str] = Field(default="", alias="osBuild")
    client_headers: Optional[Dict[str, str]] = Field(default_factory=dict, alias="clientHeaders")

    class Config:
        populate_by_name = True # Allows using either alias or field name for population
        extra = 'ignore' # Ignore extra fields passed during initialization


class ClientOpts(HttpOpts):
    base_url: Optional[HttpUrl] = Field(default="https://api.granola.ai", alias="baseUrl")


# API Response/Payload Models (examples, expand as needed based on actual API schema)

class Workspace(BaseModel):
    id: str
    name: str
    role: Optional[str] = None # Example field

class WorkspaceResponse(BaseModel):
    workspaces: List[Workspace]

class Document(BaseModel):
    document_id: str = Field(..., alias="id") # Assuming API might use camelCase
    title: str | None = None
    workspace_id: str | None = Field(..., alias="workspace_id")
    created_at: str = Field(..., alias="created_at")
    updated_at: str = Field(..., alias="updated_at")

    user_id: str | None = Field(default=None, alias="user_id")
    notes_markdown: str | None = Field(default=None, alias="notes_markdown")
    notes_plain: str | None = Field(default=None, alias="notes_plain")
    overview: str | None = Field(default=None)

    class Config:
        populate_by_name = True
        extra = 'ignore'

class DocumentsResponse(BaseModel):
    docs: List[Document]
    next_cursor: Optional[str] = Field(None, alias="next_cursor")

    class Config:
        populate_by_name = True
        extra = 'ignore'


class Person(BaseModel):
    id: str
    name: str
    email: str
    details: Optional[Dict[str, Any]] = None

class PeopleResponse(BaseModel):
    people: List[Person]

class FeatureFlagsResponse(BaseModel):
    flags: Dict[str, bool]

class NotionWorkspace(BaseModel):
    id: str
    name: str

class NotionIntegrationResponse(BaseModel):
    connected: bool
    workspaces: Optional[List[NotionWorkspace]] = None

class Subscription(BaseModel):
    id: str
    plan_type: str = Field(..., alias="planType")
    status: str
    current_period_end: str = Field(..., alias="currentPeriodEnd")
    workspace_id: Optional[str] = Field(None, alias="workspaceId")
    canceled_at: Optional[str] = Field(None, alias="canceledAt")

    class Config:
        populate_by_name = True

class SubscriptionsResponse(BaseModel):
    subscriptions: List[Subscription]

class DocumentMetadataCreator(BaseModel): # Simplified from Person for this context if structure differs
    id: str
    name: str
    email: Optional[str] = None # Example, adjust to actual API

class DocumentMetadata(BaseModel):
    document_id: str = Field(..., alias="documentId")
    creator: DocumentMetadataCreator # Could be Person if it matches
    attendees: Optional[List[Person]] = None # Assuming attendees are Person objects
    # ... other fields

    class Config:
        populate_by_name = True


class TranscriptSegment(BaseModel):
    start_timestamp: float = Field(..., alias="startTimestamp")
    end_timestamp: float = Field(..., alias="endTimestamp")
    text: str

    class Config:
        populate_by_name = True


class PanelTemplate(BaseModel):
    id: str
    title: str
    template_type: str = Field(..., alias="templateType") # Example field name

    class Config:
        populate_by_name = True


# Payload types for update methods
class UpdateDocumentPayload(BaseModel):
    document_id: str = Field(..., alias="documentId")
    title: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None
    overview: Optional[str] = None
    notes_plain: Optional[str] = Field(None, alias="notesPlain")
    notes_markdown: Optional[str] = Field(None, alias="notesMarkdown")
    # Pydantic models are strict by default; unknown fields cause errors unless extra='allow'

    class Config:
        populate_by_name = True
        extra = 'allow' # Allows passing other arbitrary keys like in TS version

class UpdateDocumentPanelPayload(BaseModel):
    document_id: str = Field(..., alias="documentId")
    panel_id: str = Field(..., alias="panelId")
    content: Dict[str, Any]

    class Config:
        populate_by_name = True
        extra = 'allow'

# Filters for get_documents and list_all_documents
class GetDocumentsFilters(BaseModel):
    workspace_id: Optional[str] = Field(None, alias="workspaceId")
    cursor: Optional[str] = None
    limit: Optional[int] = None

    class Config:
        populate_by_name = True
        extra = 'allow' # Allow additional filter keys if API supports them
