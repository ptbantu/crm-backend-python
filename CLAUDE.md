# BANTU CRM - Development Progress

> **Auto-updated by Claude Code** - Last updated: 2026-02-25

## Current Status

**Phase**: Visa Reading Worker - Production Ready with MySQL Integration

The visa-reading worker has been successfully implemented and deployed. Core functionality includes automated Gmail attachment processing, AI-powered PDF parsing using DeepSeek, and MySQL-based state management with intelligent duplicate handling.

**Latest Achievement**: Successfully processed 6 visa emails for customer LINLIN HUANG (Passport: EQ1778662, Expiry: 2026-03-25). Worker is now running as a Kubernetes Deployment with 20-minute check intervals.

---

## Milestones (Completed)

### Visa Reading Worker - Core Implementation
- [x] **Composio Gmail Integration**: Automated email fetching with attachment detection
  - Gmail API integration via Composio toolkit (version: 20260225_01)
  - Query filter: `from:ws19930801@163.com has:attachment`
  - Handles Composio API field quirks (`successfull`, `messageId`, `attachmentList`)

- [x] **AI-Powered PDF Parsing**: DeepSeek-based document extraction
  - PDF text extraction using pdfplumber with OCR fallback (Tesseract)
  - AI extraction of: customer_name, passport_no, expiry_date
  - Handles both text-based and scanned PDFs

- [x] **MySQL Database Integration**: Stateless, production-ready storage
  - Table: `st_visa_processed_logs` - Idempotent processing tracker
  - Table: `customer_documents` - Visa document storage
  - Transaction-based saves with automatic rollback on failure
  - Connection pooling with auto-reconnect (3 retries, exponential backoff)

- [x] **Intelligent Duplicate Handling**:
  - Skip successfully processed emails (idempotent)
  - Retry failed emails automatically
  - For same passport number: keep visa with furthest expiry date

- [x] **Kubernetes Deployment**: Long-running service with graceful shutdown
  - Deployment type: Kubernetes Deployment (not CronJob)
  - Graceful shutdown: SIGTERM/SIGINT signal handlers
  - Termination grace period: 30 seconds
  - Health checks: Liveness and readiness probes
  - Stateless design: No volume mounts required

- [x] **Production Configuration**:
  - Check interval: 1200 seconds (20 minutes)
  - Max emails per run: 50
  - Urgency threshold: 7 days
  - Environment-based configuration (no hardcoded secrets)

---

## Active Sprint (Todo)

### Phase 1: Monitoring & Alerting
- [ ] Add Prometheus metrics endpoint for worker monitoring
- [ ] Implement email notification for expiring visas (< 7 days)
- [ ] Create Grafana dashboard for processing statistics

### Phase 2: Enhanced Features
- [ ] Customer ID auto-linking based on passport number
- [ ] Multi-language OCR support (Indonesian, Chinese)
- [ ] Webhook support for real-time processing triggers

### Phase 3: Integration
- [ ] WeChat/WhatsApp notification integration
- [ ] API endpoint for manual visa document upload
- [ ] Admin dashboard for visa status overview

---

## Infrastructure

### Kubernetes Configuration
- **Namespace**: `default`
- **Deployment**: `visa-reading-worker`
- **Image**: `bantu-crm-visa-reading:latest`
- **Replicas**: 1 (single instance to avoid conflicts)
- **Resources**:
  - Requests: 256Mi memory, 200m CPU
  - Limits: 512Mi memory, 500m CPU

### Secrets & ConfigMaps
- **Secret**: `visa-reading-secret`
  - COMPOSIO_API_KEY
  - COMPOSIO_ENTITY_ID
  - OPENAI_API_KEY

- **Secret**: `mysql-secret`
  - MYSQL_USER
  - MYSQL_PASSWORD

- **ConfigMap**: `mysql-config`
  - DB_HOST
  - DB_PORT
  - DB_NAME

### Database Schema
```sql
-- Processing log table (idempotent tracking)
st_visa_processed_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email_id VARCHAR(255) UNIQUE,
  passport_no VARCHAR(100),
  customer_name VARCHAR(255),
  processed_at DATETIME,
  status VARCHAR(50),  -- 'success' or 'failed'
  error_message TEXT
)

-- Visa document storage
customer_documents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  customer_id INT,
  customer_name VARCHAR(255),
  document_type VARCHAR(50),  -- 'visa'
  document_number VARCHAR(100),  -- passport_no
  expiry_date DATE,
  created_at DATETIME,
  updated_at DATETIME
)
```

### External Services
- **Composio API**: `https://backend.composio.dev`
  - Entity ID: `pg-test-69d49a5d-5542-4097-bc2f-f2a974534d59`
  - Gmail toolkit version: `20260225_01`

- **DeepSeek API**: `https://api.deepseek.com`
  - Model: `deepseek-chat`
  - Temperature: 0.1 (for consistent extraction)

### Persistent Storage
- **None required** - Fully stateless design
- All state stored in MySQL database
- No local file dependencies (removed `processed_emails.json`)

---

## Recent Changes

### 2026-02-25 - Visa Reading Worker v1.0
- Migrated from JSON file storage to MySQL database
- Implemented intelligent duplicate handling (keep furthest expiry date)
- Fixed Composio API field name issues (`successfull`, `messageId`, `attachmentList`)
- Changed from CronJob to Deployment for continuous operation
- Added graceful shutdown with signal handlers
- Removed duplicate log outputs
- Updated check interval to 20 minutes (1200 seconds)
- Successfully processed 6 test emails for LINLIN HUANG

---

## Known Issues & Limitations

### Network Connectivity
- **Issue**: Intermittent connection errors to Composio API
- **Status**: Mitigated with retry mechanism (3 attempts, exponential backoff)
- **Impact**: Occasional failed check cycles, but recovers automatically

### DNS Resolution
- **Issue**: Some pods occasionally resolve external domains to 127.0.0.1
- **Status**: Monitoring, appears to be transient
- **Workaround**: Retry mechanism handles temporary failures

---

## Development Guidelines

### Before Git Commit
1. Update this CLAUDE.md file with changes
2. Test locally if possible
3. Commit with descriptive message
4. Include Co-Authored-By: Claude Sonnet 4.5

### Deployment Process
```bash
# Build Docker image
cd worker/visa-reading
docker build -t bantu-crm-visa-reading:latest .

# Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml
kubectl rollout restart deployment/visa-reading-worker

# Check status
kubectl get pods -l app=visa-reading-worker
kubectl logs -l app=visa-reading-worker --tail=50 -f
```

### Monitoring Commands
```bash
# Check processing logs
kubectl exec <pod-name> -- python3 -c "
from database import DatabaseManager
db = DatabaseManager()
# Query st_visa_processed_logs
"

# View recent visa documents
kubectl exec <pod-name> -- python3 -c "
from database import DatabaseManager
db = DatabaseManager()
# Query customer_documents
"
```

---

## Contact & Resources

- **Project Repository**: `github.com:ptbantu/crm-backend-python.git`
- **Current Branch**: `dev`
- **Latest Commit**: `2579201` - feat: add visa-reading worker with MySQL integration
- **Documentation**: See `worker/visa-reading/README.md` for detailed worker documentation
