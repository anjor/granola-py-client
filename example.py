import asyncio
from granola_client import GranolaClient

# Make your main function async
async def main():
    client = GranolaClient() # Assuming default init is okay, or provide token/opts
    print("\nAttempting to get documents directly...")
    try:
        # Await the async method
        # Get documents directly without workspace filters
        documents_response = await client.get_documents()
        print("\nDocuments Response (Pydantic Model):")
        print(documents_response)

        if documents_response and documents_response.docs:
            print(f"\nFound {len(documents_response.docs)} documents:")
            for doc in documents_response.docs:
                print(f"  - ID: {doc.document_id}, Title: {doc.title}")
                transcript = await client.get_transcript(doc.document_id)
                print(f"    Transcript: {transcript}")
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
