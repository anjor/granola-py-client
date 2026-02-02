import json
import platform
from pathlib import Path
from typing import Optional, AsyncGenerator, Tuple, cast, List, Dict, Any
import logging

from pydantic import HttpUrl, BaseModel, ValidationError

from .http_client import HttpClient
from .types import (
    ClientOpts,  # These are now Pydantic models
    Document,
    DocumentsResponse,
    DocumentMetadata,
    TranscriptSegment,
    PanelTemplate,
    NotionIntegrationResponse,
    SubscriptionsResponse,
    UpdateDocumentPayload,
    UpdateDocumentPanelPayload,
    GetDocumentsFilters,
    Person,
    FeatureFlag,
    # Types for helper methods
    DocumentSetResponse,
    DocumentListsResponse,
    EnhancedGetDocumentsFilters,
    # New types for discovered endpoints
    UserInfo,
    Workspace,
    WorkspaceMember,
    CalendarEvent,
    CreateDocumentPayload,
    CreateDocumentResponse,
    DocumentAccessUser,
    CreateFolderResponse,
    SearchResult,
    SaveToNotionResponse,
    SlackIntegrationResponse,
    SlackChannel,
)
from .pagination import paginate, PaginatedResponse
from .errors import GranolaAuthError, GranolaValidationError

logger = logging.getLogger(__name__)


class GranolaClient:
    http: HttpClient

    def __init__(self, token: Optional[str] = None, opts: Optional[ClientOpts] = None):
        # opts can be a dict or ClientOpts instance. Pydantic handles validation.
        # If opts is None, ClientOpts() provides defaults.
        client_options = ClientOpts.model_validate(opts if opts is not None else {})

        self.http = HttpClient(
            token=token,
            base_url=cast(
                HttpUrl, client_options.base_url
            ),  # base_url is HttpUrl from ClientOpts
            opts=client_options,  # Pass the validated Pydantic model
        )

        if not token:
            if platform.system() == "Darwin":
                self.http.set_token_provider(self._provide_auth_token_macos)
            else:
                logger.warning(
                    "Automatic token retrieval is macOS only. Provide token manually."
                )

    async def _provide_auth_token_macos(self) -> str:
        tokens = await GranolaClient.get_auth_tokens()
        return tokens[0]

    @staticmethod
    async def get_auth_tokens() -> Tuple[str, str]:
        if platform.system() != "Darwin":
            raise GranolaAuthError("Automatic token extraction is macOS only.")
        try:
            supabase_file_path = (
                Path.home() / "Library/Application Support/Granola/supabase.json"
            )
            if not supabase_file_path.exists():
                raise GranolaAuthError(f"Token file not found: {supabase_file_path}")

            data = json.loads(supabase_file_path.read_text(encoding="utf-8"))

            # Try WorkOS tokens first (newer auth), fall back to Cognito tokens
            if "workos_tokens" in data:
                workos_tokens = json.loads(data["workos_tokens"])
                access = workos_tokens.get("access_token")
                refresh = workos_tokens.get("refresh_token")
                if access and refresh:
                    logger.debug("Using WorkOS tokens for authentication")
                    return access, refresh

            # Fall back to Cognito tokens
            cognito_tokens = json.loads(data["cognito_tokens"])
            access, refresh = (
                cognito_tokens["access_token"],
                cognito_tokens["refresh_token"],
            )
            if not access or not refresh:
                raise GranolaAuthError("Access or refresh token missing.")
            logger.debug("Using Cognito tokens for authentication")
            return access, refresh
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get auth tokens: {e}", exc_info=True)
            raise GranolaAuthError(f"Failed to extract auth tokens: {e}") from e

    async def get_documents(
        self, filters: Optional[GetDocumentsFilters] = None
    ) -> DocumentsResponse:
        payload = (
            filters.model_dump(by_alias=True, exclude_none=True) if filters else {}
        )
        return await self.http._request_model(
            "POST",
            "/v2/get-documents",
            response_model=DocumentsResponse,
            payload_dict=payload,
        )

    async def list_all_documents(
        self, filters: Optional[GetDocumentsFilters] = None
    ) -> AsyncGenerator[Document, None]:
        initial_filters_dict = (
            filters.model_dump(by_alias=True, exclude_none=True, exclude={"cursor"})
            if filters
            else {}
        )

        async def fetch_page_func(
            cursor: Optional[str] = None,
        ) -> PaginatedResponse[Document]:
            current_filters_payload = {**initial_filters_dict}
            if cursor:
                current_filters_payload["cursor"] = cursor

            # get_documents expects GetDocumentsFilters model or dict.
            # Since we constructed a dict, we pass it directly.
            # The response from get_documents is DocumentsResponse.
            # We need to adapt it to PaginatedResponse[Document].
            docs_response = await self.http._request_model(
                "POST",
                "/v2/get-documents",
                response_model=DocumentsResponse,  # This has docs and next_cursor
                payload_dict=current_filters_payload,
            )
            return PaginatedResponse[Document](
                items=docs_response.docs, next_cursor=docs_response.next_cursor
            )

        async for doc in paginate(fetch_page_func):
            yield doc

    async def get_document_metadata(self, document_id: str) -> DocumentMetadata:
        return await self.http._request_model(
            "POST",
            "/v1/get-document-metadata",
            response_model=DocumentMetadata,
            payload_dict={"document_id": document_id},
        )

    async def get_document_transcript(
        self, document_id: str
    ) -> List[TranscriptSegment]:
        # Assuming the API returns a direct list of segments, not nested in a model.
        # If it's nested, e.g. {"segments": [...]}, then define a wrapper Pydantic model.
        # For now, let's assume _request_raw and parse manually if it's a direct list.
        # This is a common pattern Pydantic v2 handles with RootModel or TypeAdapter.
        # A simpler way if http_client always returns a model:
        class TranscriptResponse(
            BaseModel
        ):  # Temporary wrapper if API returns {"transcript": [...]} or similar
            items: List[
                TranscriptSegment
            ]  # Or RootModel[List[TranscriptSegment]] if it's just a list

        # If API directly returns a JSON list `[...]`
        # Use TypeAdapter for direct list parsing
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[TranscriptSegment])

        response = await self.http._request_raw(
            "POST",
            "/v1/get-document-transcript",
            body_data={"document_id": document_id},
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    async def update_document(self, payload: UpdateDocumentPayload) -> None:
        await self.http._request_void(
            "POST", "/v1/update-document", payload_model=payload
        )

    async def update_document_panel(self, payload: UpdateDocumentPanelPayload) -> None:
        await self.http._request_void(
            "POST", "/v1/update-document-panel", payload_model=payload
        )

    async def get_panel_templates(self) -> List[PanelTemplate]:
        # The API returns a list.
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[PanelTemplate])
        response = await self.http._request_raw(
            "POST", "/v1/get-panel-templates", body_data={}
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    async def get_people(self) -> List["Person"]:
        # API returns a list, not an object with 'people' key.
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[Person])
        response = await self.http._request_raw("POST", "/v1/get-people", body_data={})
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    async def get_feature_flags(self) -> List["FeatureFlag"]:
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[FeatureFlag])
        response = await self.http._request_raw(
            "POST", "/v1/get-feature-flags", body_data={}
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    async def get_notion_integration(self) -> NotionIntegrationResponse:
        return await self.http._request_model(
            "POST",
            "/v1/get-notion-integration",
            response_model=NotionIntegrationResponse,
            payload_dict={},
        )

    async def get_subscriptions(self) -> SubscriptionsResponse:
        return await self.http._request_model(
            "POST",
            "/v1/get-subscriptions",
            response_model=SubscriptionsResponse,
            payload_dict={},
        )

    async def refresh_google_events(self) -> None:
        await self.http._request_void(
            "POST", "/v1/refresh-google-events", payload_dict={}
        )

    async def check_for_update(self) -> str:
        platform_path = "latest-mac.yml"  # Default
        system = platform.system()
        if system == "Windows":
            platform_path = "latest.yml"  # Common for Windows
        elif system == "Linux":
            platform_path = "latest-linux.yml"

        return await self.http.get_text(f"/v1/check-for-update/{platform_path}")

    async def get_document_set(self) -> DocumentSetResponse:
        """Get a lightweight index of all documents user has access to."""
        return await self.http._request_model(
            "POST",
            "/v1/get-document-set",
            response_model=DocumentSetResponse,
            payload_dict={},
        )

    async def get_document_lists(self) -> DocumentListsResponse:
        """Get metadata for all shared folders/document lists."""
        return await self.http._request_model(
            "POST",
            "/v1/get-document-lists-metadata",
            response_model=DocumentListsResponse,
            payload_dict={
                "include_document_ids": True,
                "include_only_joined_lists": False,
            },
        )

    async def get_documents_enhanced(
        self, filters: EnhancedGetDocumentsFilters
    ) -> DocumentsResponse:
        """Enhanced version of get_documents with support for shared folder features."""
        payload = filters.model_dump(by_alias=True, exclude_none=True)
        return await self.http._request_model(
            "POST",
            "/v2/get-documents",
            response_model=DocumentsResponse,
            payload_dict=payload,
        )

    async def get_documents_by_folder_id(self, folder_id: str) -> List[Document]:
        """Get all documents from a specific shared folder/document list by ID."""
        # Get folder metadata to find document IDs
        folders_response = await self.get_document_lists()

        # Find the target folder
        target_folder = folders_response.lists.get(folder_id)
        if not target_folder:
            raise ValueError(f"Folder with ID '{folder_id}' not found")

        # Get document IDs from the folder
        document_ids = target_folder.document_ids
        if not document_ids:
            return []

        # Fetch documents with enhanced filters to get notes
        filters = EnhancedGetDocumentsFilters(
            document_ids=document_ids,
            include_last_viewed_panel=True,
            include_shared=True,
            include_folders=True,
            expand_folders=True,
            show_organization=True,
        )

        response = await self.get_documents_enhanced(filters)
        return response.docs

    async def get_documents_by_folder_name(
        self, folder_name: str, case_sensitive: bool = False
    ) -> List[Document]:
        """Get all documents from a specific shared folder/document list by name."""
        # Get folder metadata
        folders_response = await self.get_document_lists()

        # Find folder(s) by name
        matching_folders = []
        for folder_id, folder_data in folders_response.lists.items():
            if case_sensitive:
                if folder_data.title == folder_name:
                    matching_folders.append((folder_id, folder_data))
            else:
                if folder_data.title.lower() == folder_name.lower():
                    matching_folders.append((folder_id, folder_data))

        if not matching_folders:
            raise ValueError(f"No folder found with name '{folder_name}'")
        elif len(matching_folders) > 1:
            folder_titles = [f.title for _, f in matching_folders]
            raise ValueError(
                f"Multiple folders found with name '{folder_name}': {folder_titles}. "
                "Use get_documents_by_folder_id() with a specific folder ID instead."
            )

        # Use the single matching folder
        folder_id, _ = matching_folders[0]
        return await self.get_documents_by_folder_id(folder_id)

    # ============ User Info ============

    async def get_user_info(self) -> UserInfo:
        """Get information about the current authenticated user."""
        return await self.http._request_model(
            "POST",
            "/v1/get-user-info",
            response_model=UserInfo,
            payload_dict={},
        )

    # ============ Workspaces ============

    async def get_workspaces(self) -> List[Workspace]:
        """Get all workspaces the user has access to."""
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[Workspace])
        response = await self.http._request_raw(
            "POST", "/v1/get-workspaces", body_data={}
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    async def get_workspace_members(self, workspace_id: str) -> List[WorkspaceMember]:
        """Get members of a workspace."""
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[WorkspaceMember])
        response = await self.http._request_raw(
            "POST",
            "/v1/get-workspace-members",
            body_data={"workspace_id": workspace_id},
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    # ============ Calendar Events ============

    async def get_google_events(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> List[CalendarEvent]:
        """Get Google Calendar events.

        Args:
            start_date: Optional ISO date string for start of range
            end_date: Optional ISO date string for end of range
        """
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[CalendarEvent])
        payload: Dict[str, Any] = {}
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date

        response = await self.http._request_raw(
            "POST", "/v1/get-google-events", body_data=payload
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    # ============ Document CRUD ============

    async def create_document(
        self, payload: CreateDocumentPayload
    ) -> CreateDocumentResponse:
        """Create a new document."""
        return await self.http._request_model(
            "POST",
            "/v1/create-document",
            response_model=CreateDocumentResponse,
            payload_model=payload,
        )

    async def delete_document(self, document_id: str) -> None:
        """Permanently delete a document (hard delete)."""
        await self.http._request_void(
            "POST",
            "/v1/hard-delete-document",
            payload_dict={"document_id": document_id},
        )

    # ============ Document Sharing ============

    async def share_document(
        self, document_id: str, user_emails: List[str], role: str = "viewer"
    ) -> None:
        """Share a document with users by email.

        Args:
            document_id: The document to share
            user_emails: List of email addresses to share with
            role: Permission level (viewer, editor, etc.)
        """
        await self.http._request_void(
            "POST",
            "/v1/add-users-to-document",
            payload_dict={
                "document_id": document_id,
                "user_emails": user_emails,
                "role": role,
            },
        )

    async def unshare_document(self, document_id: str, user_emails: List[str]) -> None:
        """Remove users' access to a document.

        Args:
            document_id: The document to unshare
            user_emails: List of email addresses to remove
        """
        await self.http._request_void(
            "POST",
            "/v1/remove-users-from-document",
            payload_dict={
                "document_id": document_id,
                "user_emails": user_emails,
            },
        )

    async def get_document_collaborators(
        self, document_id: str
    ) -> List[DocumentAccessUser]:
        """Get users who have access to a document."""
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[DocumentAccessUser])
        response = await self.http._request_raw(
            "POST",
            "/v1/get-users-with-access",
            body_data={"document_id": document_id},
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    # ============ Folder Management ============

    async def create_folder(
        self,
        title: str,
        description: Optional[str] = None,
        workspace_id: Optional[str] = None,
        visibility: str = "private",
    ) -> CreateFolderResponse:
        """Create a new shared folder (document list).

        Args:
            title: Name of the folder
            description: Optional description
            workspace_id: Optional workspace to create in
            visibility: 'private', 'workspace', or 'public'
        """
        payload: Dict[str, Any] = {"title": title, "visibility": visibility}
        if description:
            payload["description"] = description
        if workspace_id:
            payload["workspace_id"] = workspace_id

        return await self.http._request_model(
            "POST",
            "/v1/create-document-list-v2",
            response_model=CreateFolderResponse,
            payload_dict=payload,
        )

    async def delete_folder(self, folder_id: str) -> None:
        """Delete a shared folder (document list)."""
        await self.http._request_void(
            "POST",
            "/v1/delete-document-list-v2",
            payload_dict={"document_list_id": folder_id},
        )

    async def update_folder(
        self,
        folder_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[str] = None,
    ) -> None:
        """Update a folder's metadata."""
        payload: Dict[str, Any] = {"document_list_id": folder_id}
        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if visibility:
            payload["visibility"] = visibility

        await self.http._request_void(
            "POST", "/v1/update-document-list", payload_dict=payload
        )

    async def add_document_to_folder(
        self, folder_id: str, document_id: str
    ) -> None:
        """Add a document to a shared folder."""
        await self.http._request_void(
            "POST",
            "/v1/add-document-to-list",
            payload_dict={
                "document_list_id": folder_id,
                "document_id": document_id,
            },
        )

    async def remove_document_from_folder(
        self, folder_id: str, document_id: str
    ) -> None:
        """Remove a document from a shared folder."""
        await self.http._request_void(
            "POST",
            "/v1/remove-document-from-list",
            payload_dict={
                "document_list_id": folder_id,
                "document_id": document_id,
            },
        )

    # ============ Search ============

    async def search(
        self,
        query: str,
        limit: int = 10,
        workspace_id: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
    ) -> List[SearchResult]:
        """Search documents using semantic embeddings.

        Args:
            query: Search query text
            limit: Maximum number of results
            workspace_id: Optional workspace to search within
            document_ids: Optional list of document IDs to search within
        """
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[SearchResult])
        payload: Dict[str, Any] = {"query": query, "limit": limit}
        if workspace_id:
            payload["workspace_id"] = workspace_id
        if document_ids:
            payload["document_ids"] = document_ids

        response = await self.http._request_raw(
            "POST", "/v1/search-embeddings", body_data=payload
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    # ============ Notion Integration ============

    async def save_to_notion(
        self,
        document_id: str,
        workspace_id: Optional[str] = None,
        parent_page_id: Optional[str] = None,
    ) -> SaveToNotionResponse:
        """Export a document to Notion.

        Args:
            document_id: The document to export
            workspace_id: Optional Notion workspace ID
            parent_page_id: Optional parent page in Notion
        """
        payload: Dict[str, Any] = {"document_id": document_id}
        if workspace_id:
            payload["workspace_id"] = workspace_id
        if parent_page_id:
            payload["parent_page_id"] = parent_page_id

        return await self.http._request_model(
            "POST",
            "/v1/save-to-notion",
            response_model=SaveToNotionResponse,
            payload_dict=payload,
        )

    # ============ Slack Integration ============

    async def get_slack_integration(self) -> SlackIntegrationResponse:
        """Get Slack integration status and channels."""
        return await self.http._request_model(
            "POST",
            "/v1/get-slack-integration",
            response_model=SlackIntegrationResponse,
            payload_dict={},
        )

    async def list_slack_channels(self) -> List[SlackChannel]:
        """List available Slack channels."""
        from pydantic import TypeAdapter

        ta = TypeAdapter(List[SlackChannel])
        response = await self.http._request_raw(
            "POST", "/v1/list-slack-channels", body_data={}
        )
        response_content = await response.aread()
        try:
            return ta.validate_json(response_content)
        except ValidationError as e:
            err_text = response_content.decode(
                response.encoding or "utf-8", errors="replace"
            )
            raise GranolaValidationError(
                str(e), validation_errors=e.errors(), response_text=err_text
            )

    async def post_to_slack(
        self,
        channel_id: str,
        document_id: str,
        message: Optional[str] = None,
    ) -> None:
        """Post a document to a Slack channel.

        Args:
            channel_id: Slack channel ID
            document_id: Document to share
            message: Optional message to include
        """
        payload: Dict[str, Any] = {
            "channel_id": channel_id,
            "document_id": document_id,
        }
        if message:
            payload["message"] = message

        await self.http._request_void(
            "POST", "/v1/post-slack-message", payload_dict=payload
        )

    async def close(self) -> None:
        await self.http.close()

    async def __aenter__(self) -> "GranolaClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
