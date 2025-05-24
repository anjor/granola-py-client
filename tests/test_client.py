from dotenv import load_dotenv

import pytest
import os

from granola_client import GranolaClient

load_dotenv()

@pytest.mark.asyncio
async def test_get_documents_and_metadata():
    token = os.getenv("GRANOLA_TOKEN", None)
    async with GranolaClient(token=token) as client:
        docs_response = await client.get_documents()
        assert docs_response.docs, "Should return at least one document"
        first_doc = docs_response.docs[0]
        assert hasattr(first_doc, "document_id")

        # Fetch metadata
        meta = await client.get_document_metadata(first_doc.document_id)
        # The server response does not echo document_id, so we test for creator presence instead
        assert meta.creator is not None

        # Fetch transcript
        transcript = await client.get_document_transcript(first_doc.document_id)
        assert isinstance(transcript, list)

@pytest.mark.asyncio
async def test_get_people():
    token = os.getenv("GRANOLA_TOKEN", None)
    async with GranolaClient(token=token) as client:
        resp = await client.get_people()
        assert isinstance(resp, list)
        assert len(resp) > 0
        assert hasattr(resp[0], "id")
        assert hasattr(resp[0], "name")

@pytest.mark.asyncio
async def test_get_feature_flags():
    token = os.getenv("GRANOLA_TOKEN", None)
    async with GranolaClient(token=token) as client:
        flags = await client.get_feature_flags()
        assert isinstance(flags, list)
        assert len(flags) > 0
        assert hasattr(flags[0], "feature")
        assert hasattr(flags[0], "value")

@pytest.mark.asyncio
async def test_get_panel_templates():
    token = os.getenv("GRANOLA_TOKEN", None)
    async with GranolaClient(token=token) as client:
        templates = await client.get_panel_templates()
        assert isinstance(templates, list)
        assert hasattr(templates[0], "id")
        assert hasattr(templates[0], "title")

@pytest.mark.asyncio
async def test_get_subscriptions():
    token = os.getenv("GRANOLA_TOKEN", None)
    async with GranolaClient(token=token) as client:
        subscriptions = await client.get_subscriptions()
        assert hasattr(subscriptions, "active_plan_id")
        assert hasattr(subscriptions, "subscription_plans")
        assert isinstance(subscriptions.subscription_plans, list)
