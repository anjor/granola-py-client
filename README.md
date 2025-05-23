# Granola Python Client

A Python client for the [Granola API](https://granola.ai/), inspired by the [typescript client](https://github.com/mikedemarais/granola-ts-client/tree/master). This client allows programmatic interaction with Granola's note-taking and meeting management platform. It uses `Pydantic` for robust data validation and `httpx` for asynchronous HTTP requests. It can also mimic the official Granola desktop application headers to help bypass "Unsupported client" validation.

## Features

*   Async operations using `httpx` and `asyncio`.
*   **Runtime data validation and serialization using Pydantic models.**
*   Automatic token retrieval from local Granola app (macOS only).
*   Mimics official client headers.
*   Retry mechanism for requests.
*   Pagination support for listing resources like documents.

## Requirements

*   Python 3.13+
*   `uv` (for package management, recommended)

## Installation

It's recommended to use `uv` for managing dependencies in a virtual environment.

1.  **Install `uv`**:
    Follow the official instructions: [https://github.com/astral-sh/uv#installation](https://github.com/astral-sh/uv#installation)
    ```bash
    # Example for macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clone the repository (if developing or installing from source):**
    ```bash
    git clone <repository_url> # Replace with your repo URL
    cd granola-python-client
    ```

3.  **Create and activate a virtual environment using `uv`:**
    ```bash
    uv venv
    source .venv/bin/activate  # macOS/Linux
    # .venv\Scripts\activate    # Windows
    ```

4.  **Install the package and its dependencies using `uv`:**
    For regular use:
    ```bash
    uv pip install -e .  # For editable install from local source
    ```
    For development (including test dependencies):
    ```bash
    uv pip install -e ".[dev]"
    ```
    Or, if published to PyPI in the future:
    ```bash
    # uv pip install granola-client
    ```

## Quick Start
```python
import asyncio
import platform
from granola_client import GranolaClient, ClientOpts, GranolaAuthError, DocumentsResponse

async def main():
    client = None
    try:
        api_token = "your-api-token" # Replace or use macOS auto-retrieval

        if platform.system() == "Darwin" and api_token == "your-api-token":
            print("Attempting to initialize client with automatic token retrieval (macOS)...")
            client = GranolaClient()
        else:
            if api_token == "your-api-token":
                 print("Placeholder token detected. Please set a real token or run on macOS for auto-retrieval.")
                 return
            client = GranolaClient(token=api_token)

        # Get documents
        print("\nRetrieving documents...")
        documents_response: DocumentsResponse = await client.get_documents()
        if documents_response and documents_response.docs:
            print(f"Found {len(documents_response.docs)} documents:")
            for doc in documents_response.docs:
                print(f"  - ID: {doc.document_id}, Title: {doc.title}")
        else:
            print("No documents found or response was empty.")

    except GranolaAuthError as e:
        print(f"Authentication Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if client:
            await client.close()

if __name__ == "__main__":
    asyncio.run(main())
