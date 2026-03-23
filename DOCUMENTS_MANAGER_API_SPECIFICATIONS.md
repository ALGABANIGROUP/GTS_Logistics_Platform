# 🔧 Documents Manager Bot - Backend API Specifications

**Status**: Ready for Phase 3 Implementation  
**Framework**: FastAPI (Python)  
**Database**: PostgreSQL  
**Total Endpoints**: 20  

---

## 📋 API OVERVIEW

### Base URL (Development)
```
http://localhost:8000/api/v1/documents
```

### Base URL (Production)
```
https://api.gtslogistics.com/api/v1/documents
```

### Authentication
```
Authorization: Bearer <JWT_TOKEN>
```

---

## 📚 ENDPOINT SPECIFICATIONS

### 1. DOCUMENT MANAGEMENT (5 Endpoints)

#### 1.1 Upload Document
```http
POST /api/v1/documents/upload
Content-Type: multipart/form-data

Parameters:
  file: File (required)
  document_type: string (optional) - one of: bill_of_lading, invoice, packing_list, customs, insurance, other
  metadata: JSON (optional) - custom metadata

Response (201 Created):
{
  "id": "doc_12345",
  "name": "BOL-2024-001.pdf",
  "type": "bill_of_lading",
  "status": "uploaded",
  "size": 2428800,
  "uploaded_at": "2024-01-15T10:30:00Z",
  "thumbnail_url": "/documents/doc_12345/thumbnail"
}

Errors:
  400: Invalid file type
  413: File too large
  422: Validation error
```

#### 1.2 Get Documents List
```http
GET /api/v1/documents?page=1&limit=50&status=processed&type=invoice

Parameters:
  page: int (default: 1)
  limit: int (default: 50, max: 500)
  status: string (optional) - uploaded, processing, processed, failed, archived
  type: string (optional) - document type filter
  search: string (optional) - search by name
  sort_by: string (default: uploaded_at) - field to sort by
  sort_order: string (default: desc) - asc or desc

Response (200 OK):
{
  "documents": [
    {
      "id": "doc_1",
      "name": "Bill of Lading.pdf",
      "type": "bill_of_lading",
      "status": "processed",
      "size": 2428800,
      "uploaded_at": "2024-01-15T10:30:00Z",
      "uploaded_by": "user@gts.com",
      "thumbnail_url": "/documents/doc_1/thumbnail"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 3,
  "limit": 50
}

Errors:
  401: Unauthorized
  403: Forbidden
```

#### 1.3 Get Single Document
```http
GET /api/v1/documents/{document_id}

Response (200 OK):
{
  "id": "doc_1",
  "name": "Bill of Lading.pdf",
  "type": "bill_of_lading",
  "status": "processed",
  "size": 2428800,
  "uploaded_at": "2024-01-15T10:30:00Z",
  "uploaded_by": "user@gts.com",
  "file_url": "/documents/doc_1/download",
  "metadata": {},
  "extracted_data": null,
  "compliance_status": "pending",
  "digital_signatures": []
}

Errors:
  404: Document not found
  401: Unauthorized
```

#### 1.4 Update Document
```http
PUT /api/v1/documents/{document_id}
Content-Type: application/json

Parameters:
  name: string (optional)
  type: string (optional)
  metadata: JSON (optional)
  tags: array (optional)

Response (200 OK):
{
  "id": "doc_1",
  "name": "Updated Name.pdf",
  "type": "invoice",
  "updated_at": "2024-01-15T11:30:00Z"
}

Errors:
  404: Document not found
  400: Invalid data
```

#### 1.5 Delete Document
```http
DELETE /api/v1/documents/{document_id}

Response (204 No Content):
[empty body]

Errors:
  404: Document not found
  403: Permission denied
```

---

### 2. PROCESSING (2 Endpoints)

#### 2.1 Process OCR
```http
POST /api/v1/documents/{document_id}/ocr
Content-Type: application/json

Parameters:
  language: string (default: "eng") - e.g., "eng", "ara", "fra"
  accuracy_threshold: float (default: 0.85) - minimum accuracy 0-1
  extract_tables: boolean (default: true)
  extract_handwriting: boolean (default: false)

Response (202 Accepted):
{
  "id": "ocr_task_123",
  "document_id": "doc_1",
  "status": "processing",
  "started_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:35:00Z",
  "progress": 0
}

Polling for results:
GET /api/v1/documents/{document_id}/ocr-results/{ocr_task_id}

Final Response:
{
  "id": "ocr_task_123",
  "document_id": "doc_1",
  "status": "completed",
  "extracted_data": {
    "shipper": "ABC Manufacturing",
    "consignee": "XYZ Logistics",
    "amount": "$12,500.00",
    "fields": [...]
  },
  "accuracy": 0.975,
  "completed_at": "2024-01-15T10:35:30Z"
}

Errors:
  404: Document not found
  400: Invalid parameters
  422: OCR processing failed
```

#### 2.2 Check Compliance
```http
POST /api/v1/documents/{document_id}/compliance
Content-Type: application/json

Parameters:
  standards: array (optional) - ["GDPR", "HIPAA", "SOC2", "ISO27001"]
  scan_deep: boolean (default: false) - perform deep compliance scan

Response (202 Accepted):
{
  "id": "compliance_task_123",
  "document_id": "doc_1",
  "status": "processing",
  "standards": ["GDPR", "HIPAA"],
  "progress": 0
}

Polling for results:
GET /api/v1/documents/{document_id}/compliance-results/{compliance_task_id}

Final Response:
{
  "id": "compliance_task_123",
  "document_id": "doc_1",
  "status": "completed",
  "compliant": true,
  "score": 95.5,
  "standards": {
    "GDPR": { "compliant": true, "score": 95 },
    "HIPAA": { "compliant": true, "score": 96 }
  },
  "issues": [
    {
      "severity": "warning",
      "code": "MISSING_PII_NOTICE",
      "message": "Missing PII handling notice"
    }
  ],
  "completed_at": "2024-01-15T10:40:00Z"
}

Errors:
  404: Document not found
  400: Invalid standards
```

---

### 3. SEARCH & EXPORT (3 Endpoints)

#### 3.1 Search Documents
```http
GET /api/v1/documents/search?query=invoice&filters[type]=invoice&filters[status]=processed

Parameters:
  query: string (required) - search term
  filters[type]: string (optional)
  filters[status]: string (optional)
  filters[date_from]: ISO8601 (optional)
  filters[date_to]: ISO8601 (optional)
  page: int (default: 1)
  limit: int (default: 50)

Response (200 OK):
{
  "results": [
    {
      "id": "doc_1",
      "name": "Invoice 2024-001.pdf",
      "type": "invoice",
      "relevance": 0.95,
      "snippet": "...invoice for shipment...",
      "matched_fields": ["name", "extracted_data"]
    }
  ],
  "total": 25,
  "page": 1,
  "pages": 1
}

Errors:
  400: Invalid query
  401: Unauthorized
```

#### 3.2 Export Documents
```http
POST /api/v1/documents/export
Content-Type: application/json

Parameters:
  document_ids: array (required) - list of document IDs
  format: string (required) - "pdf", "csv", "excel", "json"
  include_metadata: boolean (default: true)
  include_extracted_data: boolean (default: true)

Response (202 Accepted):
{
  "id": "export_task_123",
  "status": "processing",
  "format": "pdf",
  "document_count": 5,
  "estimated_size": "15.2 MB",
  "download_url": null,
  "expires_at": "2024-01-16T10:30:00Z"
}

Polling for results:
GET /api/v1/documents/export-status/{export_task_id}

Final Response:
{
  "id": "export_task_123",
  "status": "completed",
  "format": "pdf",
  "download_url": "/documents/exports/export_123.pdf",
  "file_size": "15248576",
  "created_at": "2024-01-15T10:35:00Z",
  "expires_at": "2024-01-16T10:35:00Z"
}

Errors:
  404: Documents not found
  400: Invalid format
  413: Export too large
```

#### 3.3 Download Document
```http
GET /api/v1/documents/{document_id}/download

Response (200 OK):
[Binary file content]

Headers:
  Content-Type: application/pdf
  Content-Disposition: attachment; filename="document.pdf"
  Content-Length: 2428800

Errors:
  404: Document not found
  403: Permission denied
```

---

### 4. DIGITAL SIGNING (2 Endpoints)

#### 4.1 Sign Document
```http
POST /api/v1/documents/{document_id}/sign
Content-Type: application/json

Parameters:
  signature_data: string (required) - base64 encoded signature
  signature_type: string (required) - "draw", "type", "upload"
  certificate_id: string (optional) - digital certificate ID
  password: string (required for type signatures)
  timestamp: ISO8601 (optional) - signing timestamp

Response (201 Created):
{
  "signature_id": "sig_123",
  "document_id": "doc_1",
  "signed_by": "user@gts.com",
  "signed_at": "2024-01-15T10:30:00Z",
  "signature_type": "draw",
  "verification_hash": "sha256_hash_here",
  "status": "pending_verification",
  "expires_at": "2025-01-15T10:30:00Z"
}

Errors:
  404: Document not found
  400: Invalid signature data
  422: Signing failed
```

#### 4.2 Verify Signature
```http
GET /api/v1/documents/{document_id}/verify-signature/{signature_id}

Response (200 OK):
{
  "signature_id": "sig_123",
  "document_id": "doc_1",
  "is_valid": true,
  "verification_hash": "sha256_hash_here",
  "signed_by": "user@gts.com",
  "signed_at": "2024-01-15T10:30:00Z",
  "verified_at": "2024-01-15T10:31:00Z",
  "signature_type": "draw",
  "certificate_status": "valid",
  "certificate_expires": "2025-01-15",
  "audit_trail": [
    {
      "action": "signature_created",
      "timestamp": "2024-01-15T10:30:00Z",
      "user": "user@gts.com"
    }
  ]
}

Errors:
  404: Signature not found
  400: Verification failed
```

---

### 5. WORKFLOWS (3 Endpoints)

#### 5.1 Get Workflow Templates
```http
GET /api/v1/documents/workflows/templates

Parameters:
  category: string (optional) - "import", "export", "customs", "all"

Response (200 OK):
{
  "templates": [
    {
      "id": "template_1",
      "name": "Standard Import",
      "description": "Process incoming shipment documents",
      "category": "import",
      "steps": [
        {
          "id": 1,
          "name": "Upload Document",
          "type": "trigger",
          "config": {}
        },
        {
          "id": 2,
          "name": "Process OCR",
          "type": "action",
          "config": { "language": "eng" }
        }
      ],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}

Errors:
  401: Unauthorized
```

#### 5.2 Create Workflow
```http
POST /api/v1/documents/workflows
Content-Type: application/json

Parameters:
  name: string (required)
  description: string (optional)
  template_id: string (optional) - use template as base
  steps: array (required) - workflow step definitions
  enabled: boolean (default: true)
  schedule: string (optional) - cron expression for automation

Response (201 Created):
{
  "id": "workflow_123",
  "name": "My Custom Workflow",
  "description": "Custom document processing",
  "status": "active",
  "steps": [...],
  "created_at": "2024-01-15T10:30:00Z",
  "created_by": "user@gts.com"
}

Errors:
  400: Invalid workflow definition
  422: Workflow validation failed
```

#### 5.3 Execute Workflow
```http
POST /api/v1/documents/{document_id}/workflow/{workflow_id}/execute
Content-Type: application/json

Parameters:
  async: boolean (default: true)

Response (202 Accepted):
{
  "execution_id": "exec_123",
  "workflow_id": "workflow_123",
  "document_id": "doc_1",
  "status": "processing",
  "started_at": "2024-01-15T10:30:00Z",
  "progress": 0,
  "current_step": 1
}

Polling for results:
GET /api/v1/documents/workflow-execution/{execution_id}

Final Response:
{
  "execution_id": "exec_123",
  "workflow_id": "workflow_123",
  "document_id": "doc_1",
  "status": "completed",
  "progress": 100,
  "results": {
    "step_1": { "status": "completed", "duration": 1500 },
    "step_2": { "status": "completed", "duration": 3200 }
  },
  "completed_at": "2024-01-15T10:33:00Z"
}

Errors:
  404: Workflow or document not found
  400: Invalid workflow state
```

---

### 6. BATCH OPERATIONS (3 Endpoints)

#### 6.1 Batch Upload
```http
POST /api/v1/documents/batch/upload
Content-Type: multipart/form-data

Parameters:
  files: File[] (required) - multiple files
  document_type: string (optional)
  auto_process: boolean (default: false)

Response (202 Accepted):
{
  "batch_id": "batch_123",
  "file_count": 5,
  "status": "uploading",
  "progress": 0,
  "created_at": "2024-01-15T10:30:00Z"
}

Polling for results:
GET /api/v1/documents/batch-status/{batch_id}

Final Response:
{
  "batch_id": "batch_123",
  "status": "completed",
  "file_count": 5,
  "successful": 4,
  "failed": 1,
  "documents": [
    { "id": "doc_1", "name": "file1.pdf", "status": "uploaded" }
  ],
  "errors": [
    { "file": "file5.pdf", "error": "Invalid format" }
  ]
}

Errors:
  400: Invalid files
  413: Batch too large
```

#### 6.2 Batch Process
```http
POST /api/v1/documents/batch/process
Content-Type: application/json

Parameters:
  document_ids: array (required)
  process_type: string (required) - "ocr", "compliance", "all"
  configuration: JSON (optional)

Response (202 Accepted):
{
  "batch_id": "batch_task_123",
  "document_count": 10,
  "process_type": "ocr",
  "status": "processing",
  "progress": 0
}

Polling for results:
GET /api/v1/documents/batch-process-status/{batch_id}

Final Response:
{
  "batch_id": "batch_task_123",
  "status": "completed",
  "processed": 10,
  "successful": 10,
  "failed": 0,
  "results": [
    {
      "document_id": "doc_1",
      "status": "completed",
      "duration": 2500
    }
  ]
}

Errors:
  404: Documents not found
  400: Invalid process type
```

#### 6.3 Batch Export
```http
POST /api/v1/documents/batch/export
Content-Type: application/json

Parameters:
  document_ids: array (required)
  format: string (required) - "pdf", "csv", "excel", "json"
  combine: boolean (default: false) - combine into single file

Response (202 Accepted):
{
  "export_id": "export_batch_123",
  "document_count": 5,
  "format": "pdf",
  "status": "processing",
  "progress": 0
}

Polling for results:
GET /api/v1/documents/batch-export-status/{export_id}

Final Response:
{
  "export_id": "export_batch_123",
  "status": "completed",
  "format": "pdf",
  "file_count": 1,
  "total_size": "15248576",
  "download_url": "/documents/exports/batch_export_123.zip",
  "expires_at": "2024-01-16T10:30:00Z"
}

Errors:
  404: Documents not found
  400: Invalid format
  413: Export too large
```

---

### 7. AUDIT & MONITORING (0 endpoints - uses existing logs)

Uses existing GTS authentication system for audit logging.

---

## 🔐 ERROR RESPONSES

### Standard Error Format
```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "The requested document does not exist",
    "status": 404,
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req_123"
  }
}
```

### Common Status Codes
- `200 OK` - Successful GET/PUT/DELETE
- `201 Created` - Successful POST (resource created)
- `202 Accepted` - Async task accepted
- `204 No Content` - Successful DELETE (no response body)
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - File/request too large
- `422 Unprocessable Entity` - Validation failed
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service down

---

## 🔗 WEBHOOK INTEGRATIONS

### Webhook Events
```
document.uploaded
document.processed
ocr.completed
compliance.completed
signature.created
workflow.completed
```

### Webhook Payload
```json
{
  "event": "document.uploaded",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "document_id": "doc_1",
    "name": "Document.pdf",
    "size": 2428800
  }
}
```

---

## 📊 DATABASE SCHEMA (Reference)

### Documents Table
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  type VARCHAR(50),
  status VARCHAR(50),
  size BIGINT,
  file_path VARCHAR(500),
  uploaded_by UUID,
  uploaded_at TIMESTAMP,
  updated_at TIMESTAMP,
  metadata JSONB,
  created_at TIMESTAMP
);
```

### OCR Tasks Table
```sql
CREATE TABLE ocr_tasks (
  id UUID PRIMARY KEY,
  document_id UUID,
  status VARCHAR(50),
  extracted_data JSONB,
  accuracy FLOAT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

### Compliance Tasks Table
```sql
CREATE TABLE compliance_tasks (
  id UUID PRIMARY KEY,
  document_id UUID,
  status VARCHAR(50),
  compliance_score FLOAT,
  standards JSONB,
  issues JSONB,
  started_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

### Digital Signatures Table
```sql
CREATE TABLE digital_signatures (
  id UUID PRIMARY KEY,
  document_id UUID,
  signature_data TEXT,
  signature_type VARCHAR(50),
  signed_by UUID,
  signed_at TIMESTAMP,
  verification_hash VARCHAR(255),
  is_valid BOOLEAN,
  verified_at TIMESTAMP
);
```

### Workflows Table
```sql
CREATE TABLE workflows (
  id UUID PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  steps JSONB,
  status VARCHAR(50),
  created_by UUID,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

---

## 🧪 TESTING ENDPOINTS

### Using cURL

```bash
# List documents
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/documents

# Upload document
curl -F "file=@document.pdf" \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/v1/documents/upload

# Process OCR
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"language": "eng"}' \
  http://localhost:8000/api/v1/documents/doc_1/ocr
```

### Using Python (FastAPI Test Client)

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test upload
response = client.post(
    "/api/v1/documents/upload",
    files={"file": open("document.pdf", "rb")},
    headers={"Authorization": f"Bearer {token}"}
)
assert response.status_code == 201
```

---

## 📝 IMPLEMENTATION PRIORITY

### Phase 1 (Must Have)
1. Document management (upload, list, get, delete)
2. Search functionality
3. Export functionality

### Phase 2 (Should Have)
4. OCR processing
5. Compliance checking
6. Digital signing

### Phase 3 (Nice to Have)
7. Workflows
8. Batch operations
9. Advanced analytics

---

**Next Step**: Implement these endpoints in FastAPI  
**Estimated Time**: 2-3 weeks  
**Dependencies**: PostgreSQL, SQLAlchemy, Celery for async tasks
