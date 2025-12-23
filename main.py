
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import uuid
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('/mnt/c/Users/HP/projects/ithute-ai-bridge-268e1-firebase-adminsdk-fbsvc-a730777e08.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

# Initialize the FastAPI app
app = FastAPI(
    title="AI BRIDGE Data Ingestion API",
    description="API for collecting educational text data for bias reduction.",
    version="1.0.0",
)

# Pydantic model for a single data item
class IngestItem(BaseModel):
    raw_text: str
    language: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Pydantic model for the request body (a list of items)
class IngestPayload(BaseModel):
    items: List[IngestItem]

@app.post("/ingest")
async def ingest_data(payload: IngestPayload):
    """
    Accepts a list of text data items and processes them.
    This is the endpoint the scraper will send data to.
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="No items provided for ingestion.")

    processed_count = 0
    collection_ref = db.collection('ingested_data')

    # Use a batch write for efficiency when inserting multiple documents
    batch = db.batch()

    for item in payload.items:
        # Generate a unique content_id
        content_id = str(uuid.uuid4())
        record = {
            "raw_text": item.raw_text,
            "language": item.language,
            "source": item.source,
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": item.metadata,
            "processing_status": "raw"
        }
        
        # Add the document to the batch
        doc_ref = collection_ref.document(content_id)
        batch.set(doc_ref, record)
        processed_count += 1
    
    # Commit the batch
    batch.commit()
    print(f"Successfully processed and saved {processed_count} items to Firestore.")

    return {
        "message": f"Successfully ingested {processed_count} items.",
        "status": "success"
    }

@app.get("/")
async def root():
    return {"message": "Welcome to the AI BRIDGE Ingestion API"}