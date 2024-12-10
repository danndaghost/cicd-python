# test_pinecone.py
from dotenv import load_dotenv
import os
from pinecone import Pinecone, ServerlessSpec
import time

# Load .env file - add this at the beginning
load_dotenv()

def test_pinecone_setup():
    try:
        # Get API key from .env
        api_key = os.getenv("PINECONE_API_KEY")
        
        if not api_key:
            raise ValueError("PINECONE_API_KEY not found in .env file")
            
        # Initialize Pinecone client
        pc = Pinecone(
            api_key=api_key
        )
        
        # List existing indexes
        print("Existing indexes:", pc.list_indexes().names())
        
        index_name = 'quickstart'
        
        # Check if index exists and create if it doesn't
        if index_name not in pc.list_indexes().names():
            print(f"Creating new index: {index_name}")
            
            # Create the index
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric='euclidean',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            # Wait for index to be ready
            print("Waiting for index to be ready...")
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(5)
            
        # Get and print index details
        index_description = pc.describe_index(index_name)
        print("\nIndex details:")
        print(f"Name: {index_description.name}")
        print(f"Dimension: {index_description.dimension}")
        print(f"Metric: {index_description.metric}")
        print(f"Status: {index_description.status}")
        
        # Test index connection
        index = pc.Index(index_name)
        
        print("\nSuccessfully connected to the index!")
        
        return index
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_pinecone_setup()