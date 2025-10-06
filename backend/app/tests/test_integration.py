import os
import pytest
from fastapi.testclient import TestClient
from ..main import app

# Use a test-specific database
TEST_DB = "./test_kaas.db"
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB}'
os.environ['CHROMA_DB_DIR'] = './test_chroma_db'
os.environ['GROQ_API_KEY'] = ''
os.environ['HF_FALLBACK'] = 'true'

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_and_teardown():
    # Setup: ensure clean state before tests
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    # The lifespan event in main.py will create the DB

    yield

    # Teardown: clean up after tests
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # A more thorough teardown would also clean the test_chroma_db directory

def test_upload_and_query():
    """
    A simple integration test to upload a sample file and then query it.
    """
    # 1. Upload the sample resume 
    sample_file_path = "sample_data/sample_resume.txt"
    with open(sample_file_path,"rb") as f:
        response = client.post("/upload", files={"file": ("sample_resume.txt", f, "text/plain")})
    
    assert response.status_code == 202
    upload_data = response.json()
    assert "upload_id" in upload_data
    assert upload_data["filename"] == "sample_resume.txt"

    # It's a background task, so we need to wait a bit for ingestion to complete
    import time
    time.sleep(5)

    # 2. Query the uploaded document
    query_payload = {"question": "Where did Alex Doe work before Innovatech Solutions?"}
    response = client.post("/query", json=query_payload)

    assert response.status_code == 200
    query_data = response.json()

    # Assertions on the response structure
    assert "answer" in query_data
    assert "sources" in query_data
    assert query_data["query"] == query_payload["question"]

    # Assertions on the content (can be brittle with generative models)
    # We check for key terms instead of an exact match.
    answer = query_data["answer"].lower()
    print(f"Generated Answer: {answer}")
    assert "techgen" in answer or "techgen corp" in answer

    # Assertions on the source
    assert len(query_data["sources"]) > 0
    source = query_data["sources"][0]
    assert source["filename"] == "sample_resume.txt"
    assert "TechGen Corp" in source["Snippet"]
