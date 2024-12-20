import logging
import os
import qdrant_client
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
from dotenv import load_dotenv
# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Define Qdrant URL and API key
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
QDRANT_URL = os.getenv('QDRANT_URL')

# Create a custom session with retries
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)

# Create the Qdrant client
qclient = qdrant_client.QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=15
)

# Test connection or perform operations
try:
    collections = qclient.get_collections()
    print("Successfully connected to Qdrant!")
except Exception as e:
    print(f"Error: {e}")
