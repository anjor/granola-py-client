import asyncio
from granola_client import GranolaClient

# Make your main function async
async def main():
    client = GranolaClient() # Assuming default init is okay, or provide token/opts
    print("Attempting to get workspaces...")
    try:
        # Await the async method
        workspaces_response = await client.get_workspaces()
        print("\nWorkspaces Response (Pydantic Model):")
        print(workspaces_response)

        if workspaces_response and workspaces_response.workspaces:
            print(f"\nFound {len(workspaces_response.workspaces)} workspaces:")
            for ws in workspaces_response.workspaces:
                print(f"  - ID: {ws.id}, Name: {ws.name}, Role: {ws.role}")
        else:
            print("No workspaces found or response was empty.")

        # Get documents directly without workspace filters
        print("\nAttempting to get documents directly...")
        documents_response = await client.get_documents()
        print("\nDocuments Response (Pydantic Model):")
        print(documents_response)

        if documents_response and documents_response.docs:
            print(f"\nFound {len(documents_response.docs)} documents:")
            for doc in documents_response.docs:
                print(f"  - ID: {doc.document_id}, Title: {doc.title}")
        else:
            print("No documents found or response was empty.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.close()
        print("\nClient session closed.")


if __name__ == "__main__":
    # Run the async main function using asyncio.run()
    asyncio.run(main())
