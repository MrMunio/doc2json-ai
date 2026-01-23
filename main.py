import os
import uuid
import json
import logging
import base64
import zlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Any, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import aioboto3

# Import generalized components
from utils.data_extractor import GenericDataExtractor
from utils.db_client import DatabaseClient
from utils.schema_utils import DynamicModelBuilder

load_dotenv()

# Configuration from .env
APPLICATION_ID = os.getenv("APPLICATION_ID", "generic_data_extractor")
MODEL_ID = os.getenv("MODEL_ID", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "100000"))
TOKEN_OVERLAP = int(os.getenv("TOKEN_OVERLAP", "500"))
RESPONSE_SCHEMA_PATH = os.getenv("RESPONSE_SCHEMA_PATH", "contract_model.schema.json")

DB_SCHEMA = os.getenv("DB_SCHEMA", "public")
TEMP_FOLDER = "temp_uploads"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# S3 Configuration
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_KEY_PREFIX = f"{APPLICATION_ID}_files/"

# Status Constants
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_INPROGRESS = "inprogress"
STATUS_INITIATED = "initiated"
VALID_STATUSES = [STATUS_SUCCESS, STATUS_FAILED, STATUS_INPROGRESS, STATUS_INITIATED]

# Global Clients
db_client = None
s3_session = None
s3_client = None
response_model = None
extractor = None

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log", encoding="utf-8")],
)
logger = logging.getLogger(__name__)

# Pydantic Models for API
class UploadResponse(BaseModel):
    request_id: str
    message: str
    status: str

class StatusResponse(BaseModel):
    request_id: str
    metadata: dict
    status: str
    extracted_data: Optional[dict] = None
    message: Optional[str] = None
    errors: Optional[dict] = None
    created_at: str
    updated_at: str

# Helper Functions
def calculate_crc32(content: bytes) -> int:
    return zlib.crc32(content) & 0xFFFFFFFF

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_client, s3_session, s3_client, response_model, extractor
    try:
        # Load Dynamic Model
        logger.info(f"Loading schema from: {RESPONSE_SCHEMA_PATH}")
        response_model = DynamicModelBuilder.build_model_from_schema(RESPONSE_SCHEMA_PATH)
        
        # Validate Model against OpenAI Strict Mode
        DynamicModelBuilder.validate_model(response_model)

        
        # Initialize Database
        db_client = DatabaseClient(schema=DB_SCHEMA)
        if await db_client.test_connection():
            logger.info("Database connection established")
        else:
            logger.error("Database connection failed")
        
        # Initialize S3 (Optional)
        if AWS_ACCESS_KEY and AWS_SECRET_KEY and S3_BUCKET_NAME:
            s3_session = aioboto3.Session()
            s3_client = await s3_session.client(
                's3',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            ).__aenter__()
            logger.info("S3 client initialized")
        else:
            logger.warning("AWS credentials not found. S3 storage will be skipped.")
            
        # Initialize GenericDataExtractor
        logger.info(f"Initializing GenericDataExtractor with model={MODEL_ID}")
        extractor = GenericDataExtractor(
            model_id=MODEL_ID,
            max_tokens=MAX_TOKENS,
            token_overlap=TOKEN_OVERLAP,
            response_model=response_model,
            ocr_method="vlm" # "vlm" or "tesseract"
        )
        await extractor.initialize()
        logger.info("GenericDataExtractor initialized successfully")

    except Exception as e:
        logger.error(f"Lifespan startup failed: {e}")
        raise

    yield

    if db_client:
        await db_client.dispose()
    if s3_client:
        await s3_client.__aexit__(None, None, None)
    if extractor:
        await extractor.close()

app = FastAPI(title="Generic Data Extractor", version="2.0.0", lifespan=lifespan)

async def update_tracker(request_id: str, status: str, **kwargs):
    """
    Update the extraction_tracker table.
    Supported kwargs: extracted_data, message, errors, metadata
    """
    if not db_client:
        logger.error("DB client not initialized. Cannot update tracker.")
        return

    update_fields = ["status = $1", "updated_at = $2"]
    params = [status, datetime.utcnow()]
    
    idx = 3
    for key, value in kwargs.items():
        if value is not None:
            # Safety truncation for message if it's a string
            if key == "message" and isinstance(value, str) and len(value) > 2000:
                value = value[:1997] + "..."
                
            update_fields.append(f"{key} = ${idx}")
            if isinstance(value, (dict, list)):
                params.append(json.dumps(value))
            else:
                params.append(value)
            idx += 1
    
    params.append(request_id)
    query = f"UPDATE {DB_SCHEMA}.extraction_tracker SET {', '.join(update_fields)} WHERE request_id = ${idx}"
    
    try:
        await db_client.execute_non_query(query, tuple(params))
    except Exception as e:
        logger.error(f"Failed to update tracker: {e}")

async def process_background(request_id: str, file_path: str):
    logger.info(f"Starting background processing for {request_id}")
    
    if not extractor:
        logger.error("Extractor not initialized. Aborting task.")
        await update_tracker(request_id, STATUS_FAILED, message="System configuration error: Extractor not initialized")
        return

    try:
        logger.info(f"[{request_id}] Updating tracker to INPROGRESS")
        await update_tracker(request_id, STATUS_INPROGRESS, message="Processing document")
        logger.info(f"[{request_id}] Tracker updated successfully")
        
        logger.info(f"[{request_id}] Starting file processing: {file_path}")
        result = await extractor.process_file(file_path)
        logger.info(f"[{request_id}] File processing completed with status: {result.get('status')}")
        
        if result["status"] == "success":
            logger.info(f"[{request_id}] Extraction successful, updating tracker to SUCCESS")
            await update_tracker(
                request_id, 
                STATUS_SUCCESS, 
                extracted_data=result.get("data"), 
                message=result.get("message")
            )
            logger.info(f"[{request_id}] Successfully updated tracker with extracted data")
        else:
            logger.warning(f"[{request_id}] Extraction failed: {result.get('message')}")
            await update_tracker(
                request_id, 
                STATUS_FAILED, 
                extracted_data=result.get("data"), 
                message=result.get("message"),
                errors={"error": result.get("message")}
            )
            logger.info(f"[{request_id}] Tracker updated with failure status")
            
    except Exception as e:
        logger.error(f"[{request_id}] Error in background task: {e}", exc_info=True)
        await update_tracker(request_id, STATUS_FAILED, message="System error", errors={"detail": str(e)})
    finally:
        logger.info(f"[{request_id}] Cleanup started")
        if os.path.exists(file_path):
            logger.info(f"[{request_id}] Removing temporary file: {file_path}")
            os.remove(file_path)
        logger.info(f"[{request_id}] Background processing completed")

@app.post("/extract", response_model=UploadResponse, status_code=202)
async def extract_data(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")
        
        checksum = calculate_crc32(content)
        
        # Check duplicates
        if db_client:
            check_query = f"SELECT request_id, status, metadata FROM {DB_SCHEMA}.extraction_tracker WHERE application_id = $1 AND metadata->>'checksum' = $2 AND metadata->>'original_filename' = $3 ORDER BY created_at DESC LIMIT 1"
            records = await db_client.execute_query(check_query, (APPLICATION_ID, str(checksum), file.filename))
            if records:
                rec = records[0]
                status = rec["status"]
                
                # If success, return data
                if status == STATUS_SUCCESS:
                    return JSONResponse(content={
                        "request_id": str(rec["request_id"]),
                        "message": "Duplicate successful request found.",
                        "status": status,
                        "data": rec.get("extracted_data")
                    }, status_code=200)
                
                # If inprogress, skip starting new task but return 202
                if status == STATUS_INPROGRESS:
                    return JSONResponse(content={
                        "request_id": str(rec["request_id"]),
                        "message": "Extraction already in progress for this file.",
                        "status": status
                    }, status_code=202)
                
                # If initiated or failed, we allow a new attempt (proceeding below)
                logger.info(f"Existing record with status '{status}' found. Starting new extraction attempt.")

        # Storage
        temp_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        temp_filename = f"{temp_id}{file_ext}"
        file_path = os.path.join(TEMP_FOLDER, temp_filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        s3_key = None
        if s3_client:
            s3_key = f"{S3_KEY_PREFIX}{temp_filename}"
            try:
                await s3_client.put_object(Bucket=S3_BUCKET_NAME, Key=s3_key, Body=content)
            except Exception as e:
                logger.warning(f"S3 upload failed: {e}. Proceeding without S3.")
                s3_key = None

        # Init Tracker
        metadata = {
            "original_filename": file.filename,
            "checksum": str(checksum),
            "file_size": len(content),
            "s3_key": s3_key
        }
        
        request_id = None
        if db_client:
            insert_query = f"INSERT INTO {DB_SCHEMA}.extraction_tracker (application_id, metadata, status, message) VALUES ($1, $2, $3, $4) RETURNING request_id"
            rows = await db_client.execute_query(insert_query, (APPLICATION_ID, json.dumps(metadata), STATUS_INITIATED, "Initiated"))
            request_id = str(rows[0]["request_id"])
        else:
            request_id = temp_id # Fallback if no DB
            
        background_tasks.add_task(process_background, request_id, file_path)
        
        return {"request_id": request_id, "message": "Upload successful, processing started.", "status": STATUS_INITIATED}

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{request_id}", response_model=StatusResponse)
async def get_status(request_id: uuid.UUID):
    if not db_client:
        raise HTTPException(status_code=503, detail="Database not available")
    
    query = f"SELECT request_id, metadata, status, extracted_data, message, errors, created_at, updated_at FROM {DB_SCHEMA}.extraction_tracker WHERE request_id = $1"
    rows = await db_client.execute_query(query, (str(request_id),))
    if not rows:
        raise HTTPException(status_code=404, detail="Request not found")
    
    row = rows[0]
    return StatusResponse(
        request_id=str(row["request_id"]),
        metadata=row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"]),
        status=row["status"],
        extracted_data=row["extracted_data"] if isinstance(row["extracted_data"], dict) else (json.loads(row["extracted_data"]) if row["extracted_data"] else None),
        message=row["message"],
        errors=row["errors"] if isinstance(row["errors"], dict) else (json.loads(row["errors"]) if row["errors"] else None),
        created_at=row["created_at"].isoformat(),
        updated_at=row["updated_at"].isoformat()
    )

@app.get("/historical-requests")
async def get_history(limit: int = 10, offset: int = 0):
    if not db_client:
        return {"items": [], "total": 0}
    
    query = f"SELECT request_id, status, metadata, created_at FROM {DB_SCHEMA}.extraction_tracker WHERE application_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3"
    rows = await db_client.execute_query(query, (APPLICATION_ID, limit, offset))
    
    count_query = f"SELECT COUNT(*) FROM {DB_SCHEMA}.extraction_tracker WHERE application_id = $1"
    counts = await db_client.execute_query(count_query, (APPLICATION_ID,))
    
    items = []
    for r in rows:
        items.append({
            "request_id": str(r["request_id"]),
            "status": r["status"],
            "metadata": r["metadata"] if isinstance(r["metadata"], dict) else json.loads(r["metadata"]),
            "created_at": r["created_at"].isoformat()
        })
    
    return {"items": items, "total": int(counts[0]["count"])}

@app.get("/get-base64/{request_id}")
async def get_base64(request_id: uuid.UUID):
    if not s3_client:
        return {"status": "failed", "message": "S3 client not initialized. Cannot fetch file content."}
    
    try:
        # Get metadata from DB
        query = f"SELECT metadata FROM {DB_SCHEMA}.extraction_tracker WHERE request_id = $1"
        rows = await db_client.execute_query(query, (str(request_id),))
        if not rows or not rows[0]["metadata"]:
            raise HTTPException(status_code=404, detail="Request metadata not found")
        
        metadata = rows[0]["metadata"] if isinstance(rows[0]["metadata"], dict) else json.loads(rows[0]["metadata"])
        s3_key = metadata.get("s3_key")
        if not s3_key:
            return {"status": "failed", "message": "S3 key not found in metadata"}
        
        response = await s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        content = await response['Body'].read()
        return {
            "request_id": request_id,
            "filename": metadata.get("original_filename"),
            "base64_content": base64.b64encode(content).decode('utf-8'),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Download error: {e}")
        return {"status": "failed", "message": str(e)}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)