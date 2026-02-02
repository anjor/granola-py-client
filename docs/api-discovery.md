# Granola API Discovery Results

This document contains the complete list of API endpoints discovered by analyzing the Granola Electron application source code.

## Discovery Method

Endpoints were discovered by:
1. Extracting the `app.asar` archive from `/Applications/Granola.app/Contents/Resources/`
2. Searching for API URL patterns in the JavaScript bundles
3. Categorizing endpoints by functionality

## Currently Implemented in Python Client (13 endpoints)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v2/get-documents` | POST | Document listing with filters |
| `/v1/get-document-metadata` | POST | Single document metadata |
| `/v1/get-document-transcript` | POST | Transcript segments |
| `/v1/update-document` | POST | Update title/notes/overview |
| `/v1/update-document-panel` | POST | Update panel content |
| `/v1/get-document-set` | POST | Lightweight document index |
| `/v1/get-document-lists-metadata` | POST | Shared folders metadata |
| `/v1/get-people` | POST | Contacts list |
| `/v1/get-feature-flags` | POST | Feature toggles |
| `/v1/get-panel-templates` | POST | Panel templates |
| `/v1/get-notion-integration` | POST | Notion integration status |
| `/v1/get-subscriptions` | POST | Subscription info |
| `/v1/refresh-google-events` | POST | Trigger calendar refresh |
| `/v1/check-for-update/{platform}` | GET | Update check |

---

## All Discovered Endpoints (283 total)

### Documents (Core)

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-document` | **High** | Create new document |
| `/v1/upsert-document` | Medium | Create or update document |
| `/v1/hard-delete-document` | **High** | Permanently delete document |
| `/v1/get-document-status` | Medium | Check document status |
| `/v1/get-documents` | Low | v1 version (use v2) |
| `/v1/get-documents-batch` | Medium | Batch fetch documents |
| `/v1/get-documents-delta` | Low | Get document changes |
| `/v1/get-document-panels` | Medium | Get all panels for document |
| `/v1/create-document-panel` | Medium | Create new panel |
| `/v1/get-ydoc` | Low | Y.js collaborative doc |
| `/v1/insert-collaborative-documents` | Low | Collaborative editing |
| `/v1/check-document-access` | Low | Verify access permissions |
| `/v1/check-document-notification` | Low | Check notifications |
| `/v1/get-public-document-panel` | Low | Public panel access |
| `/v1/move-documents-to-workspace` | Medium | Move docs between workspaces |

### Documents Lists (Folders)

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-document-list` | **High** | Create shared folder |
| `/v1/create-document-list-v2` | **High** | Create folder (v2) |
| `/v1/delete-document-list` | **High** | Delete shared folder |
| `/v1/delete-document-list-v2` | **High** | Delete folder (v2) |
| `/v1/update-document-list` | Medium | Update folder metadata |
| `/v1/get-document-list` | Medium | Get single folder |
| `/v1/get-document-lists` | Medium | Get all folders |
| `/v2/get-document-lists` | Medium | Get folders (v2) |
| `/v1/add-document-to-list` | **High** | Add doc to folder |
| `/v1/remove-document-from-list` | **High** | Remove doc from folder |
| `/v1/batch-update-document-lists-v2` | Medium | Batch folder updates |
| `/v1/check-document-list-access` | Low | Verify folder access |
| `/v1/get-document-list-opengraph-data` | Low | OG metadata |
| `/v1/add-user-favourite-document-list` | Low | Favorite a folder |
| `/v1/remove-user-favourite-document-list` | Low | Unfavorite folder |
| `/v1/get-folder-digest` | Low | Folder summary |
| `/v1/get-folder-icon` | Low | Folder icon |
| `/v1/get-list-suggestion` | Low | AI folder suggestions |

### Document Sharing

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/add-users-to-document` | **High** | Share doc with users |
| `/v1/add-users-to-document-list` | Medium | Share folder with users |
| `/v1/add-users-to-document-list-v2` | Medium | Share folder (v2) |
| `/v1/remove-users-from-document` | **High** | Revoke doc access |
| `/v1/remove-users-from-document-list` | Medium | Revoke folder access |
| `/v1/remove-users-from-document-list-v2` | Medium | Revoke folder (v2) |
| `/v1/update-document-list-user` | Low | Update user permissions |
| `/v1/update-document-list-user-v2` | Low | Update permissions (v2) |
| `/v1/update-document-user` | Low | Update doc user perms |
| `/v1/get-users-with-access` | Medium | List doc collaborators |
| `/v1/get-users-with-access-to-list` | Medium | List folder collaborators |
| `/v1/get-shared-documents` | Medium | Get shared docs |
| `/v1/update-document-presence` | Low | Presence tracking |

### User & Account

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-user-info` | **High** | Get current user info |
| `/v1/get-user-preferences` | Medium | User settings |
| `/v1/update-user-preferences` | Medium | Update settings |
| `/v1/delete-user` | Low | Delete account |
| `/v1/set-person` | Low | Update person record |
| `/v1/list-user-sessions` | Low | Active sessions |
| `/v1/revoke-session` | Low | End a session |
| `/v1/add-user-attribution` | Low | Track attribution |
| `/v1/add-user-coupons` | Low | Add coupon codes |
| `/v1/publish-user-event` | Low | Analytics event |
| `/v1/get-email-preferences-context` | Low | Email settings |

### Workspaces

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-workspaces` | **High** | List workspaces |
| `/v2/create-workspace` | **High** | Create workspace |
| `/v1/create-workspace` | Medium | Create workspace (v1) |
| `/v1/update-workspace` | Medium | Update workspace |
| `/v1/delete-workspace` | Medium | Delete workspace |
| `/v1/get-workspace-members` | Medium | List members |
| `/v1/get-workspace-member-count` | Low | Member count |
| `/v1/add-workspace-members` | Medium | Add members |
| `/v1/set-workspace-member-statuses` | Low | Update member status |
| `/v1/set-workspace-roles` | Low | Set member roles |
| `/v1/set-workspace-company-type` | Low | Company type |
| `/v1/leave-workspace` | Medium | Leave workspace |
| `/v1/join-workspace` | Medium | Join workspace |
| `/v1/join-workspace-via-code` | Medium | Join via invite code |
| `/v1/get-workspace-for-invite-code` | Low | Get workspace info |
| `/v1/get-workspaces-for-slug` | Low | Find workspace by slug |
| `/v1/get-workspaces-notes-count` | Low | Notes count |
| `/v1/request-workspace-membership` | Low | Request to join |

### Workspace Invitations

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-workspace-invite-link` | Medium | Create invite link |
| `/v1/get-workspace-invite-links` | Medium | List invite links |
| `/v1/revoke-workspace-invite-link` | Medium | Revoke link |
| `/v1/revoke-workspace-invites` | Low | Revoke all invites |
| `/v1/get-workspace-invite-status` | Low | Check invite status |
| `/v1/send-invite-emails` | Medium | Send invites |
| `/v1/get-invite-list` | Low | List invites |

### Authentication

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/auth` | Low | Authentication endpoint |
| `/v1/auth-soft-check` | Low | Soft auth check |
| `/v1/auth-handoff-complete` | Low | Complete handoff |
| `/v1/login-check` | Low | Check login status |
| `/v1/login-complete` | Low | Complete login |
| `/v1/refresh-access-token` | Medium | Refresh token |
| `/v1/workos-auth-complete` | Low | WorkOS auth callback |

### Calendar Integration

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-google-events` | **High** | Get calendar events |
| `/v1/refresh-calendar-events` | Medium | Refresh events |
| `/v1/create-calendar-event` | Medium | Create event |
| `/v1/find-free-calendar-slots` | Medium | Find available times |
| `/v1/get-selected-calendars` | Medium | Selected calendars |
| `/v1/set-selected-calendar` | Medium | Select calendar |
| `/v1/set-selected-calendars` | Medium | Select multiple |
| `/v1/generate-calendar-addon-api-key` | Low | Calendar addon key |
| `/v1/google-calendar-webhook` | Low | Webhook handler |
| `/v1/outlook-calendar-webhook` | Low | Outlook webhook |

### Search & Embeddings

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/search-embeddings` | **High** | Semantic search |
| `/v1/generate-document-embeddings` | Medium | Generate embeddings |
| `/v1/embeddings-ada` | Low | OpenAI Ada embeddings |
| `/v1/turbopuffer-index-documents` | Low | Index documents |
| `/v1/turbopuffer-index-documents-generator` | Low | Index generator |
| `/v1/get-entity-batch` | Low | Batch entity fetch |
| `/v1/get-entity-set` | Low | Entity set |

### Integrations - Notion

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/save-to-notion` | **High** | Export to Notion |
| `/v1/delete-notion-integration` | Medium | Disconnect Notion |
| `/v1/notion-oauth-callback` | Low | OAuth callback |

### Integrations - Slack

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-slack-integration` | Medium | Slack status |
| `/v1/delete-slack-integration` | Medium | Disconnect Slack |
| `/v1/post-slack-message` | **High** | Send to Slack |
| `/v1/list-slack-channels` | Medium | List channels |
| `/v1/create-slack-channel` | Medium | Create channel |
| `/v1/slack-oauth-callback` | Low | OAuth callback |
| `/v1/slack-webhook-handler` | Low | Webhook handler |

### Integrations - HubSpot

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-hubspot-integration` | Medium | HubSpot status |
| `/v1/update-hubspot-integration` | Medium | Update settings |
| `/v1/delete-hubspot-integration` | Medium | Disconnect |
| `/v1/hubspot-oauth-callback` | Low | OAuth callback |

### Integrations - Salesforce

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-salesforce-integration` | Medium | Salesforce status |
| `/v1/delete-salesforce-integration` | Medium | Disconnect |
| `/v1/salesforce-oauth-callback` | Low | OAuth callback |

### Integrations - Attio

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-attio-integration` | Medium | Attio status |
| `/v1/create-attio-note` | Medium | Create Attio note |
| `/v1/delete-attio-integration` | Medium | Disconnect |
| `/v1/search-attio-records` | Medium | Search records |
| `/v1/get-attio-list-preference` | Low | List preferences |
| `/v1/set-attio-list-preference` | Low | Set preferences |
| `/v1/attio-oauth-callback` | Low | OAuth callback |

### Integrations - Zapier

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-zapier-connections` | Medium | Zapier connections |
| `/v1/add-zapier-connection` | Medium | Add connection |
| `/v1/delete-zapier-connection` | Medium | Delete connection |
| `/v1/get-folder-zapier-integrations` | Low | Folder integrations |
| `/v1/update-folder-zapier-integration` | Low | Update integration |
| `/v1/proxy-zapier-webhook` | Low | Webhook proxy |

### Integrations - General

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-integrations` | Medium | All integrations |
| `/v1/save-to-integration` | Medium | Export to integration |
| `/v1/search-integration` | Low | Search integration |
| `/v1/upsert-integrations` | Low | Upsert integrations |

### Integrations - Affinity

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/affinity` | Low | Affinity integration |

### Integrations - Airtable

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/airtable` | Low | Airtable integration |

### Transcription

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/transcribe-audio` | Medium | Transcribe audio |
| `/v1/generate-transcript` | Medium | Generate transcript |
| `/v1/insert-transcriptions` | Low | Insert transcriptions |
| `/v1/delete-transcription-chunks` | Low | Delete chunks |
| `/v1/get-transcription-auth-token` | Low | Auth token |
| `/v1/get-deepgram-token` | Low | Deepgram token |
| `/v1/transcription-webhook-handler` | Low | Webhook handler |

### AI Chat & LLM

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/llm-proxy` | Medium | LLM proxy |
| `/v1/llm-process-attachments` | Low | Process attachments |
| `/v1/get-chat-models` | Low | Available models |
| `/v1/get-chat-citation` | Low | Get citation |

### Streaming Endpoints (stream.api.granola.ai)

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/chat-with-documents` | **High** | AI chat with docs |
| `/v1/chat-with-documents-v2` | **High** | Chat v2 |
| `/v1/chat-with-documents-web` | Medium | Web chat |
| `/v1/generate-content-stream` | **High** | Generate content |
| `/v1/get-documents-batch-stream` | Medium | Batch stream |
| `/v1/llm-proxy-stream` | Medium | LLM streaming |
| `/v1/pre-meeting-brief` | Medium | Pre-meeting brief |
| `/v1/view-source-summary-web` | Low | Source summary |
| `/v1/agent-status` | Low | Agent status |
| `/v1/mcp-server` | Low | MCP server |

### Recipes (Templates)

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-recipes` | Medium | Get recipes |
| `/v1/upsert-recipe` | Medium | Create/update recipe |
| `/v1/delete-recipe` | Medium | Delete recipe |
| `/v1/get-recipe-web` | Low | Web recipe view |
| `/v1/get-recipe-opengraph-data` | Low | Recipe OG data |
| `/v1/track-recipe-usage` | Low | Track usage |
| `/v1/update-user-saved-recipe` | Low | Save recipe |

### Subscriptions & Billing

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-subscription` | Low | Create subscription |
| `/v1/get-current-subscription` | Medium | Current subscription |
| `/v1/subscription-plan` | Low | Plan details |
| `/v1/get-subscription-checkout-status` | Low | Checkout status |
| `/v1/create-shared-checkout-session` | Low | Shared checkout |
| `/v1/follow-shared-checkout-session` | Low | Follow checkout |
| `/v1/get-free-trial-data` | Low | Trial info |
| `/v1/get-offer` | Low | Offers |
| `/v1/request-offer-pack-coupon-code` | Low | Coupon request |
| `/v1/validate-promo-code` | Low | Validate promo |
| `/v1/stripe-event-handler` | Low | Stripe webhook |

### Attachments & Files

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-attachments` | Medium | Get attachments |
| `/v1/delete-attachments` | Medium | Delete attachments |
| `/v1/process-attachments` | Low | Process files |
| `/v1/get-file-upload-url` | Medium | Upload URL |
| `/v1/upload-file` | Medium | Upload file |
| `/v1/request-audio-upload-url` | Low | Audio upload URL |
| `/v1/create-plain-attachment-upload-url` | Low | Plain upload URL |

### Phone Integration

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/phone-get-numbers` | Low | Get phone numbers |
| `/v1/phone-generate-token` | Low | Generate token |
| `/v1/phone-start-verification` | Low | Start verification |
| `/v1/phone-check-verification` | Low | Check verification |
| `/v1/phone-delete-number` | Low | Delete number |
| `/v1/phone-call-status` | Low | Call status |
| `/v1/phone-blocked-regions` | Low | Blocked regions |
| `/v1/phone-verification-callback` | Low | Verification callback |
| `/v1/phone-webhook-handler` | Low | Phone webhook |
| `/v1/twilio-alarms-webhook` | Low | Twilio alarms |

### Consent & Privacy

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-affirmative-consent` | Low | Create consent |
| `/v1/log-consent-event` | Low | Log event |
| `/v1/sync-consent-event` | Low | Sync event |
| `/v1/get-consent-redirect-data` | Low | Redirect data |
| `/v1/get-privacy-mode` | Low | Privacy mode |
| `/v1/set-privacy-mode` | Low | Set privacy |

### API Keys

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-public-api-key` | Medium | Create API key |
| `/v1/get-public-api-keys` | Medium | List API keys |
| `/v1/revoke-public-api-key` | Medium | Revoke key |

### MCP (Model Context Protocol)

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/mcp-info` | Low | MCP info |
| `/v1/mcp-registry` | Low | MCP registry |
| `/v1/mcp-oauth-start` | Low | OAuth start |
| `/v1/mcp-oauth-callback` | Low | OAuth callback |
| `/v1/manage-mcp-token` | Low | Manage token |

### Cloud Agent

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/cloud-agent` | Low | Cloud agent |
| `/v1/cloud-agent-connector` | Low | Connector |
| `/v1/cloud-agent-oauth-callback` | Low | OAuth callback |
| `/v1/get-cloud-agent-connectors` | Low | Get connectors |
| `/v1/disconnect-cloud-agent-connector` | Low | Disconnect |

### Wiki

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/generate-wiki-page` | Low | Generate page |
| `/v1/get-wiki-page` | Low | Get page |

### Notifications (Knock)

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/get-knock-user-token` | Low | Knock token |
| `/v1/knock-webhook-handler` | Low | Webhook handler |
| `/v1/set-notification-device-token` | Low | Device token |
| `/v1/send-notes-notification` | Low | Send notification |

### Data Export & Transfer

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/create-data-export` | Medium | Create export |
| `/v1/transfer-notes` | Low | Transfer notes |
| `/v1/request-transfer-notes` | Low | Request transfer |

### Misc

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/hello` | Low | Health check |
| `/v1/catchphrase` | Low | Random catchphrase |
| `/v1/decimal` | Low | Decimal operations |
| `/v1/get-versions` | Low | App versions |
| `/v1/get-release-channels` | Low | Release channels |
| `/v1/update-release-channel` | Low | Update channel |
| `/v1/download-latest` | Low | Download Mac |
| `/v1/download-latest-windows` | Low | Download Windows |
| `/v1/send-download-email` | Low | Email download link |
| `/v1/send-internal-feedback` | Low | Internal feedback |
| `/v1/send-loops-event` | Low | Loops analytics |
| `/v1/send-pre-call-email-preview` | Low | Email preview |
| `/v1/get-crunched-data` | Low | Analytics data |
| `/v1/get-note-opengraph-data` | Low | OG data |
| `/v1/create-plain-feedback-thread` | Low | Feedback |
| `/v1/upsert-plain-customer` | Low | Plain customer |
| `/v1/plain-customer-cards` | Low | Customer cards |
| `/v1/create-tracked-link` | Low | Create link |
| `/v1/retrieve-tracked-link` | Low | Get link |
| `/v1/track-dub-lead` | Low | Track lead |
| `/v1/register-redirected-event` | Low | Track redirect |
| `/v1/store-device-session` | Low | Store session |
| `/v1/retrieve-device-session` | Low | Get session |
| `/v1/store-download-session` | Low | Download session |
| `/v1/retrieve-download-session` | Low | Get download |
| `/v1/sync-push` | Low | Sync push |
| `/v1/update-config` | Low | Update config |
| `/v1/update-document-service` | Low | Document service |
| `/v1/reset-feature-flags` | Low | Reset flags |
| `/v1/set-feature-flag` | Low | Set flag |
| `/v1/set-dotplot` | Low | Dotplot |
| `/v1/admin` | Low | Admin endpoint |

### Test/Debug Endpoints

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/test-400` | - | Test 400 error |
| `/v1/test-500` | - | Test 500 error |
| `/v1/test-exception` | - | Test exception |
| `/v1/test-call-sns` | - | Test SNS |

### WebSocket Endpoints

| Endpoint | Priority | Notes |
|----------|----------|-------|
| `/v1/websocket-connect` | Low | WebSocket connect |
| `/v1/websocket-disconnect` | Low | WebSocket disconnect |
| `/v1/websocket-default` | Low | WebSocket default |

---

## Priority Implementation Recommendations

### Phase 1: High Priority (Core Functionality)
1. `/v1/create-document` - Essential for creating new documents
2. `/v1/hard-delete-document` - Essential for document management
3. `/v1/search-embeddings` - Semantic search capability
4. `/v1/get-user-info` - User context
5. `/v1/get-workspaces` - Multi-workspace support
6. `/v1/get-google-events` - Calendar integration
7. `/v1/add-users-to-document` - Sharing
8. `/v1/remove-users-from-document` - Unsharing
9. Folder CRUD operations (`create-document-list`, `delete-document-list`, `add-document-to-list`, `remove-document-from-list`)

### Phase 2: Medium Priority (Enhanced Features)
1. Slack integration endpoints
2. Notion export (`save-to-notion`)
3. Recipe/template management
4. Transcription endpoints
5. Attachment handling
6. Calendar event creation

### Phase 3: Low Priority (Advanced/Niche)
1. Other CRM integrations (HubSpot, Salesforce, Attio)
2. Phone integration
3. MCP endpoints
4. Cloud agent
5. Wiki features

---

## Notes

- Most endpoints use POST method
- Streaming endpoints are on `stream.api.granola.ai` subdomain
- v2 endpoints generally offer enhanced functionality
- Many endpoints have v1 and v2 versions; prefer v2 when available
- Test/debug endpoints should not be implemented in production client
