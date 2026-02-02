from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict, computed_field


# Client Options
class HttpOpts(BaseModel):
    timeout: Optional[int] = 10000  # milliseconds
    retries: Optional[int] = 3
    app_version: Optional[str] = Field(default="6.531.0", alias="appVersion")
    client_type: Optional[str] = Field(
        default="electron", alias="clientType"
    )  # Consider "python-httpx"
    client_platform: Optional[str] = Field(
        default=None, alias="clientPlatform"
    )  # Will be auto-detected
    client_architecture: Optional[str] = Field(
        default=None, alias="clientArchitecture"
    )  # Will be auto-detected
    electron_version: Optional[str] = Field(default="39.2.7", alias="electronVersion")
    chrome_version: Optional[str] = Field(
        default="142.0.7444.235", alias="chromeVersion"
    )
    node_version: Optional[str] = Field(default="22.21.1", alias="nodeVersion")
    os_version: Optional[str] = Field(
        default=None, alias="osVersion"
    )  # Will be auto-detected
    os_build: Optional[str] = Field(default="", alias="osBuild")
    client_headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, alias="clientHeaders"
    )

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class ClientOpts(HttpOpts):
    base_url: Optional[HttpUrl] = Field(
        default="https://api.granola.ai", alias="baseUrl"
    )


# API Response/Payload Models (examples, expand as needed based on actual API schema)


class Document(BaseModel):
    document_id: str = Field(..., alias="id")  # Assuming API might use camelCase
    title: str | None = None
    workspace_id: str | None = Field(..., alias="workspace_id")
    created_at: str = Field(..., alias="created_at")
    updated_at: str = Field(..., alias="updated_at")

    user_id: str | None = Field(default=None, alias="user_id")
    notes_markdown: str | None = Field(default=None, alias="notes_markdown")
    notes_plain: str | None = Field(default=None, alias="notes_plain")
    overview: str | None = Field(default=None)

    # Support for shared folder notes via last_viewed_panel
    last_viewed_panel: Optional[Dict[str, Any]] = Field(
        None, alias="last_viewed_panel", repr=False
    )

    @computed_field
    @property
    def notes(self) -> str:
        """Returns the meeting notes converted from ProseMirror JSON to Markdown."""
        if not self.last_viewed_panel:
            return ""

        content = self.last_viewed_panel.get("content")
        if not content:
            return ""

        # Content should be a dict/object, not a string
        if isinstance(content, str):
            return ""

        try:
            from .utils import convert_prosemirror_to_markdown

            return convert_prosemirror_to_markdown(content)
        except Exception:
            # If conversion fails, return empty string rather than crashing
            return ""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class DocumentsResponse(BaseModel):
    docs: List[Document]
    next_cursor: Optional[str] = Field(None, alias="next_cursor")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class Person(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    details: Optional[Dict[str, Any]] = None



# The API returns a list, not an object w/ a `people` key!
PeopleResponse = List[Person]


# The API returns a list of features, not `{"flags": ...}`
class FeatureFlag(BaseModel):
    feature: str
    value: Any = None
    user_id: Optional[str] = None


FeatureFlagsResponse = List[FeatureFlag]


class NotionWorkspace(BaseModel):
    id: str
    name: str


class NotionIntegrationResponse(BaseModel):
    canIntegrate: bool
    isConnected: bool
    authUrl: Optional[str] = None
    integrations: Optional[dict] = None
    # If there are additional fields, add as needed.


class SubscriptionPlan(BaseModel):
    id: str
    type: str
    display_name: str
    price: dict
    currency_iso: str
    requires_workspace: bool
    requires_payment: bool
    privacy_mode: str
    is_team_upsell_target: bool
    features: list
    display_order: int
    live: bool


class SubscriptionsResponse(BaseModel):
    active_plan_id: Optional[str] = None
    subscription_plans: Optional[list] = None


class DocumentMetadataCreator(
    BaseModel
):  # Simplified from Person for this context if structure differs
    id: Optional[str] = None
    name: str
    email: Optional[str] = None  # Example, adjust to actual API


class DocumentMetadata(BaseModel):
    document_id: Optional[str] = Field(None, alias="document_id")
    creator: DocumentMetadataCreator  # Could be Person if it matches
    attendees: Optional[List[Person]] = None  # Assuming attendees are Person objects
    # ... other fields

    model_config = ConfigDict(populate_by_name=True)


class TranscriptSegment(BaseModel):
    start_timestamp: str = Field(..., alias="startTimestamp")
    end_timestamp: str = Field(..., alias="endTimestamp")
    text: str

    model_config = ConfigDict(populate_by_name=True)


class PanelTemplate(BaseModel):
    id: str
    title: str
    # The server may not return 'templateType', so make it optional and match what the API uses (e.g., category)
    template_type: Optional[str] = Field(
        None, alias="templateType"
    )  # If API uses category, also add:
    category: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


# Payload types for update methods
class UpdateDocumentPayload(BaseModel):
    document_id: str = Field(..., alias="documentId")
    title: Optional[str] = None
    notes: Optional[Dict[str, Any]] = None
    overview: Optional[str] = None
    notes_plain: Optional[str] = Field(None, alias="notesPlain")
    notes_markdown: Optional[str] = Field(None, alias="notesMarkdown")
    # Pydantic models are strict by default; unknown fields cause errors unless extra='allow'

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class UpdateDocumentPanelPayload(BaseModel):
    document_id: str = Field(..., alias="documentId")
    panel_id: str = Field(..., alias="panelId")
    content: Dict[str, Any]

    model_config = ConfigDict(populate_by_name=True)


# Filters for get_documents and list_all_documents
class GetDocumentsFilters(BaseModel):
    workspace_id: Optional[str] = Field(None, alias="workspaceId")
    cursor: Optional[str] = None
    limit: Optional[int] = None

    model_config = ConfigDict(populate_by_name=True, extra="allow")


# Document Set (lightweight document index)
class DocumentSetResponse(BaseModel):
    documents: Dict[str, Dict[str, Any]]  # {doc_id: {updated_at, owner}}
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# Document List (Shared Folder) Models
class DocumentListIcon(BaseModel):
    type: str
    color: str
    value: str


class DocumentListMember(BaseModel):
    user_id: str = Field(..., alias="user_id")
    name: str
    email: str
    avatar: Optional[str] = None
    role: str
    created_at: str = Field(..., alias="created_at")
    model_config = ConfigDict(populate_by_name=True)


class SlackChannel(BaseModel):
    id: str
    name: str


class DocumentList(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    icon: Optional[DocumentListIcon] = None
    visibility: str
    workspace_id: str = Field(..., alias="workspace_id")
    is_favourited: bool = Field(..., alias="is_favourited")
    user_role: Optional[str] = Field(None, alias="user_role")
    members: List[DocumentListMember]
    document_ids: List[str] = Field(..., alias="document_ids")
    slack_channel: Optional[SlackChannel] = Field(None, alias="slack_channel")
    is_shared: bool = Field(..., alias="is_shared")
    sharing_link_visibility: str = Field(..., alias="sharing_link_visibility")
    created_at: str = Field(..., alias="created_at")
    updated_at: str = Field(..., alias="updated_at")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class DocumentListsResponse(BaseModel):
    lists: Dict[str, DocumentList]
    model_config = ConfigDict(populate_by_name=True)


# Enhanced filters for get-documents with shared folder support
class EnhancedGetDocumentsFilters(GetDocumentsFilters):
    include_last_viewed_panel: Optional[bool] = Field(
        None, alias="include_last_viewed_panel"
    )
    include_shared: Optional[bool] = Field(None, alias="include_shared")
    include_folders: Optional[bool] = Field(None, alias="include_folders")
    expand_folders: Optional[bool] = Field(None, alias="expand_folders")
    show_organization: Optional[bool] = Field(None, alias="show_organization")
    document_ids: Optional[List[str]] = Field(None, alias="document_ids")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ User Info ============


class UserInfo(BaseModel):
    id: str
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="created_at")
    workspace_id: Optional[str] = Field(None, alias="workspace_id")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Workspaces ============


class WorkspaceMember(BaseModel):
    user_id: str = Field(..., alias="user_id")
    name: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="created_at")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class Workspace(BaseModel):
    id: str
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = Field(None, alias="created_at")
    updated_at: Optional[str] = Field(None, alias="updated_at")
    company_type: Optional[str] = Field(None, alias="company_type")
    member_count: Optional[int] = Field(None, alias="member_count")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WorkspacesResponse(BaseModel):
    workspaces: List[Workspace]
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class WorkspaceMembersResponse(BaseModel):
    members: List[WorkspaceMember]
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Calendar Events ============


class CalendarEventAttendee(BaseModel):
    email: str
    name: Optional[str] = None
    response_status: Optional[str] = Field(None, alias="responseStatus")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class CalendarEvent(BaseModel):
    id: str
    title: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    start_time: Optional[str] = Field(None, alias="start_time")
    end_time: Optional[str] = Field(None, alias="end_time")
    calendar_id: Optional[str] = Field(None, alias="calendar_id")
    attendees: Optional[List[CalendarEventAttendee]] = None
    meeting_link: Optional[str] = Field(None, alias="meeting_link")
    location: Optional[str] = None
    all_day: Optional[bool] = Field(None, alias="allDay")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class CalendarEventsResponse(BaseModel):
    events: List[CalendarEvent]
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Document Creation ============


class CreateDocumentPayload(BaseModel):
    title: Optional[str] = None
    workspace_id: Optional[str] = Field(None, alias="workspace_id")
    calendar_event_id: Optional[str] = Field(None, alias="calendar_event_id")
    notes: Optional[Dict[str, Any]] = None
    notes_plain: Optional[str] = Field(None, alias="notes_plain")
    notes_markdown: Optional[str] = Field(None, alias="notes_markdown")
    overview: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class CreateDocumentResponse(BaseModel):
    document_id: str = Field(..., alias="document_id")
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Document Deletion ============


class DeleteDocumentPayload(BaseModel):
    document_id: str = Field(..., alias="document_id")
    model_config = ConfigDict(populate_by_name=True)


# ============ Document Sharing ============


class ShareDocumentPayload(BaseModel):
    document_id: str = Field(..., alias="document_id")
    user_emails: List[str] = Field(..., alias="user_emails")
    role: Optional[str] = "viewer"  # viewer, editor, etc.
    model_config = ConfigDict(populate_by_name=True)


class UnshareDocumentPayload(BaseModel):
    document_id: str = Field(..., alias="document_id")
    user_emails: List[str] = Field(..., alias="user_emails")
    model_config = ConfigDict(populate_by_name=True)


class DocumentAccessUser(BaseModel):
    user_id: str = Field(..., alias="user_id")
    email: str
    name: Optional[str] = None
    role: str
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class DocumentAccessResponse(BaseModel):
    users: List[DocumentAccessUser]
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Folder Management ============


class CreateFolderPayload(BaseModel):
    title: str
    description: Optional[str] = None
    workspace_id: Optional[str] = Field(None, alias="workspace_id")
    visibility: Optional[str] = "private"  # private, workspace, public
    model_config = ConfigDict(populate_by_name=True)


class CreateFolderResponse(BaseModel):
    id: str
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class UpdateFolderPayload(BaseModel):
    document_list_id: str = Field(..., alias="document_list_id")
    title: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class AddDocumentToFolderPayload(BaseModel):
    document_list_id: str = Field(..., alias="document_list_id")
    document_id: str = Field(..., alias="document_id")
    model_config = ConfigDict(populate_by_name=True)


class RemoveDocumentFromFolderPayload(BaseModel):
    document_list_id: str = Field(..., alias="document_list_id")
    document_id: str = Field(..., alias="document_id")
    model_config = ConfigDict(populate_by_name=True)


# ============ Search ============


class SearchQuery(BaseModel):
    query: str
    limit: Optional[int] = 10
    workspace_id: Optional[str] = Field(None, alias="workspace_id")
    document_ids: Optional[List[str]] = Field(None, alias="document_ids")
    model_config = ConfigDict(populate_by_name=True)


class SearchResult(BaseModel):
    document_id: str = Field(..., alias="document_id")
    title: Optional[str] = None
    snippet: Optional[str] = None
    score: Optional[float] = None
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class SearchResponse(BaseModel):
    results: List[SearchResult]
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Notion Integration ============


class SaveToNotionPayload(BaseModel):
    document_id: str = Field(..., alias="document_id")
    workspace_id: Optional[str] = Field(None, alias="workspace_id")
    parent_page_id: Optional[str] = Field(None, alias="parent_page_id")
    model_config = ConfigDict(populate_by_name=True)


class SaveToNotionResponse(BaseModel):
    notion_page_url: Optional[str] = Field(None, alias="notion_page_url")
    success: bool
    model_config = ConfigDict(populate_by_name=True, extra="allow")


# ============ Slack Integration ============


class SlackIntegrationResponse(BaseModel):
    is_connected: bool = Field(..., alias="isConnected")
    channels: Optional[List[Dict[str, Any]]] = None
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class PostSlackMessagePayload(BaseModel):
    channel_id: str = Field(..., alias="channel_id")
    document_id: str = Field(..., alias="document_id")
    message: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class SlackChannelsResponse(BaseModel):
    channels: List[SlackChannel]
    model_config = ConfigDict(populate_by_name=True, extra="allow")
