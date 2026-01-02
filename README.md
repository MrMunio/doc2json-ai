# Doc2JSON: AI Powered Data Extraction Service

A powerful, FastAPI-based service that converts any unstructured document (PDF, DOCX, TXT) into structured JSON data using OpenAI's Structured Outputs. It dynamically builds response models from any provided JSON schema.

---

## ⚡ Quick Start (Docker Compose)

The fastest way to get the service running with its own local database.

1.  **Clone the repository** and navigate to the project folder.
2.  **Create a `.env` file** (copying from `.env.example`):
    ```bash
    cp .env.example .env
    ```
3.  **Add your OpenAI API Key** and set the model:
    ```env
    OPENAI_API_KEY=sk-proj-...
    MODEL_ID=gpt-5-mini # Recommended for large documents (>100k tokens)
    ```
    > [!TIP]
    > For best results with large documents, use `gpt-5-mini` or models with context length > 128k.
4.  **Start the application**:
    ```bash
    docker-compose up --build
    ```
5.  **Access the Services**:
    - **User Interface (Streamlit)**: `http://localhost:8501`
    - **API (FastAPI)**: `http://localhost:8021`
    - **Interactive Docs (Swagger UI)**: `http://localhost:8021/docs` (Great for "getting your hands dirty" with the API!)

---

## 🛠️ Detailed Installation & Configuration

### 1. Database Options

#### Option A: Use Internal Docker Database (Default)
The provided `docker-compose.yml` includes a PostgreSQL service.
- **Set in `.env`**:
  ```env
  DB_HOST=db
  DB_NAME=extraction_db
  DB_USER=postgres
  DB_PASSWORD=your_password
  ```
- The `app` container will automatically initialize the schema and tables on startup.

#### Option B: Use Your Own (Remote) Database
If you have an existing PostgreSQL instance (e.g., AWS RDS):
1.  **Update `.env`** with your remote credentials:
    ```env
    DB_HOST=your-rds-endpoint.aws.com
    DB_PORT=5432
    DB_NAME=your_db
    DB_USER=your_user
    DB_PASSWORD=your_password
    ```
2.  **Create the necessary table**:
    Ensure your database has the `gen_random_uuid()` extension enabled (default in PG 13+) and run:
    ```sql
    CREATE TABLE IF NOT EXISTS extraction_tracker (
        request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        application_id VARCHAR(255) NOT NULL,
        metadata JSONB NOT NULL,
        status VARCHAR(50) NOT NULL,
        extracted_data JSONB,
        message TEXT,
        errors JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_application_id ON extraction_tracker (application_id);
    CREATE INDEX IF NOT EXISTS idx_metadata_checksum ON extraction_tracker USING gin (metadata);
    ```
3.  **Disable the internal DB service** in `docker-compose.yml` or simply run the application container alone.
3.  Ensure your host can reach the remote database.

---

### 2. Storage Options (S3 vs. Local)

The service supports optional S3 integration for permanent file storage.

#### Option A: Local-Only (No S3)
If you don't provide AWS credentials, the service will only store files temporarily in `temp_uploads` during processing.
- **Set in `.env`**: Simply leave `S3_BUCKET_NAME` or `AWS_ACCESS_KEY_ID` empty/commented out.
- **Behavior**: Download/Base64 endpoints will respond with a message indicating S3 skip.

#### Option B: Enable S3 Storage
Files are uploaded to S3 immediately upon receipt, allowing for later retrieval.
- **Set in `.env`**:
  ```env
  AWS_ACCESS_KEY_ID=AKIA...
  AWS_SECRET_ACCESS_KEY=...
  S3_BUCKET_NAME=your-bucket-name
  AWS_REGION=us-east-1
  ```

---

## 🏗️ Production-Ready Architecture

This service is built for high-performance and reliable document processing at scale.

### ⚡ Optimized & Asynchronous
The entire core is built on **FastAPI** with an **asynchronous engine**, ensuring non-blocking I/O operations and high concurrency.

### 🧵 Specialized OCR Threading
To prevent system bottlenecks, normal text-based PDFs are processed instantly, while heavy image-based or scanned PDFs are offloaded to **separate processing threads**. This ensures the main application remains responsive even under heavy load.

### 🧩 Conquering the LLM Context Bottleneck
Doc2JSON AI cleverly handles documents of any size by implementing a sophisticated **Sliding Window Chunking Strategy**.
- **Configurable Context**: Tweak `MAX_TOKENS` (e.g., 100,000) and `TOKEN_OVERLAP` (e.g., 500) in your `.env` to suit your document complexity.
- **Contextual Continuity**: Each batch result is fed into the next as "previous context," ensuring extracted data remains accurate and consistent across chunk boundaries.

---

## 🖥️ User Interface

The service comes with a built-in Streamlit UI for easy interaction.

### 1. Extract Page
- Upload documents (PDF, DOCX, TXT).
- Real-time status polling for extraction results.
- View structured JSON output directly in the UI.

### 2. History Page
- View a history of all extraction requests.
- Filter and search through previous extractions.
- Re-download or view data from past requests.

---

### 3. Dynamic Schema Configuration

The core "magic" of this service is its ability to adapt to any data structure.

1.  Place your JSON schema file in the project directory (e.g., `my_schema.json`).
2.  Update `.env`:
    ```env
    RESPONSE_SCHEMA_PATH=my_schema.json
    ```
3.  Restart the service. The API will now extract data according to your new schema.

    > **📘 Need help building a schema?**  
    > See the [Schema Creation Guide](SCHEMA_CREATION_GUIDE.md) for detailed instructions on creating schemas compatible with OpenAI's Strict Mode (Structured Outputs).


---

## 📖 Environment Variables Reference

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | Your OpenAI API key | **Required** |
| `MODEL_ID` | OpenAI model to use | `gpt-4o-mini` |
| `APPLICATION_ID` | Logical ID for this instance | `generic_data_extractor` |
| `RESPONSE_SCHEMA_PATH`| Path to the JSON schema file | `contract_model.schema.json` |
| `DB_HOST` | Database hostname | `db` (for Docker) |
| `TEMP_FOLDER` | Where files are saved during upload | `temp_uploads` |

---

## 🚀 API Usage

### 📤 Upload a Document
`POST /extract` (Multipart Form Data)
- **Field**: `file` (Your document)
- **Response**: `202 Accepted` with a `request_id`.

### 🔍 Check Status
`GET /status/{request_id}`
- Returns processing status, extracted data (if successful), or error details.

### 📜 History
`GET /historical-requests`
- Returns a paginated list of previous extraction requests.

### 📄 Get Base64 Content
`GET /get-base64/{request_id}`
- Retrieves the original file from S3 and returns it as a Base64 string.

---

## 💻 Local Development (Non-Docker)

If you prefer to run natively on your machine:

1.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Initialize Database**:
    ```bash
    python init_db.py
    ```
3.  **Run the Backend (FastAPI)**:
    ```bash
    python main.py
    ```
4.  **Run the Frontend (Streamlit)**:
    ```bash
    streamlit run streamlit_app.py
    ```

---

## 💡 Pro Tip: Get Your Hands Dirty
If you're a developer looking to integrate this service or explore its full capabilities, head over to `http://localhost:8021/docs`. The **Swagger UI** allows you to test every endpoint, understand the data models, and see exactly how the "magic" happens.
