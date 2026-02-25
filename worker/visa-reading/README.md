# Visa Reading Worker

AI-powered email automation system that processes visa documents from Gmail attachments and stores them in MySQL database.

**运行模式：常驻任务（Deployment）**

## Features

- ✅ **Database-backed processing**: Uses MySQL instead of local JSON files for state management
- ✅ **Idempotent processing**: Prevents duplicate processing using `st_visa_processed_logs` table
- ✅ **Transaction safety**: Ensures data consistency with database transactions
- ✅ **AI-powered extraction**: Uses DeepSeek AI to extract visa information from PDF documents
- ✅ **OCR support**: Falls back to OCR for scanned documents
- ✅ **Kubernetes-ready**: Fully stateless, designed for Deployment (long-running service)
- ✅ **Graceful shutdown**: Handles SIGTERM/SIGINT signals properly
- ✅ **Auto-reconnect**: Database connection pool with automatic reconnection
- ✅ **Continuous mode**: Runs in a loop with configurable check interval

## Architecture

### Database Tables

**1. `st_visa_processed_logs`** (Processing Log)
- Tracks which emails have been processed
- Prevents duplicate processing
- Records processing status and errors

**2. `customer_documents`** (Visa Data)
- Stores extracted visa information
- Links to customer records
- Maintains document metadata

### Processing Flow

```
┌─────────────────────────────────────────────────────────┐
│ 启动 Worker（常驻进程）                                   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 初始化数据库表                                            │
└─────────────────────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │   主循环 (while True)      │
         └───────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 1. 获取邮件（Composio Gmail API）                        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 检查 email_id 是否在 st_visa_processed_logs 中       │
│    - 如果存在 → 跳过                                     │
│    - 如果不存在 → 继续处理                               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 3. 下载 PDF 附件                                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 提取文本（pdfplumber + OCR fallback）                │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 5. AI 解析（DeepSeek）                                   │
│    - customer_name                                       │
│    - passport_no                                         │
│    - expiry_date (YYYY-MM-DD)                           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 6. 数据库事务                                            │
│    BEGIN TRANSACTION                                     │
│    ├─ INSERT INTO customer_documents                    │
│    ├─ INSERT INTO st_visa_processed_logs                │
│    └─ COMMIT (成功) / ROLLBACK (失败)                    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ 7. 休眠 CHECK_INTERVAL_SECONDS 秒                        │
│    (分段休眠，快速响应退出信号)                           │
└─────────────────────────────────────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │   返回主循环继续执行       │
         └───────────────────────────┘
                         ↓
         ┌───────────────────────────┐
         │ 收到 SIGTERM/SIGINT?      │
         │   是 → 优雅退出            │
         │   否 → 继续循环            │
         └───────────────────────────┘
```

## Configuration

### Environment Variables

**注意：本项目使用根目录的 `.env` 文件（`../../.env`），不需要在此目录创建单独的 `.env` 文件。**

Required variables in root `.env`:

```bash
# Composio API
COMPOSIO_API_KEY=your_composio_api_key
COMPOSIO_ENTITY_ID=your_entity_id
COMPOSIO_DANGEROUSLY_SKIP_VERSION_CHECK=true

# DeepSeek AI
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com

# Visa Worker Configuration
VISA_SENDER_EMAIL=ws19930801@163.com
VISA_URGENCY_THRESHOLD_DAYS=7
VISA_MAX_EMAILS_PER_RUN=50
VISA_CHECK_INTERVAL_SECONDS=120

# Database (already configured in root .env)
DB_HOST=mysql
DB_PORT=3306
DB_NAME=bantu_crm
DB_USER=bantu_user
DB_PASSWORD=your_password
```

### Graceful Shutdown

The worker handles shutdown signals properly:

- **SIGTERM**: Sent by Kubernetes when stopping the pod
- **SIGINT**: Sent when pressing Ctrl+C

When receiving a shutdown signal:
1. Sets `shutdown_flag = True`
2. Completes current email processing
3. Closes database connections
4. Exits cleanly

**Termination Grace Period**: 30 seconds (configured in k8s-deployment.yaml)

## Local Development

### Prerequisites

- Python 3.11+
- MySQL database
- Tesseract OCR installed
- Poppler utils (for PDF processing)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment (use root .env file)
# Edit ../../.env and add Composio/OpenAI credentials
# Database credentials should already be configured

# Run the worker
python main.py
```

### Database Initialization

The worker automatically creates the `st_visa_processed_logs` table on first run:

```sql
CREATE TABLE IF NOT EXISTS `st_visa_processed_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email_id` VARCHAR(255) NOT NULL UNIQUE,
    `passport_no` VARCHAR(100) DEFAULT NULL,
    `customer_name` VARCHAR(255) DEFAULT NULL,
    `processed_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `status` VARCHAR(50) NOT NULL DEFAULT 'success',
    `error_message` TEXT DEFAULT NULL,
    INDEX `idx_email_id` (`email_id`),
    INDEX `idx_passport_no` (`passport_no`)
);
```

## Kubernetes Deployment

### Build Docker Image

```bash
docker build -t bantu-crm-visa-reading:latest .
```

### Deploy as Long-Running Service

```bash
# Apply the Deployment configuration
kubectl apply -f k8s-deployment.yaml

# Check Deployment status
kubectl get deployment visa-reading-worker

# View pods
kubectl get pods -l app=visa-reading-worker

# Check logs (follow mode)
kubectl logs -l app=visa-reading-worker --tail=50 -f
```

### Deployment Configuration

- **Type**: Deployment (long-running service)
- **Replicas**: 1 (single instance to avoid concurrent processing conflicts)
- **Restart Policy**: Always
- **Graceful Shutdown**: 30 seconds termination grace period
- **Resources**: 256Mi-512Mi memory, 200m-500m CPU
- **Health Checks**: Liveness and readiness probes

### Stateless Design

The worker is fully stateless:
- ✅ No local file storage (removed `processed_emails.json`)
- ✅ No volume mounts required
- ✅ All state stored in MySQL database
- ✅ Graceful shutdown on SIGTERM/SIGINT
- ✅ Auto-reconnect on database connection loss

## Monitoring

### Check Processing Status

```sql
-- View recent processing logs
SELECT * FROM st_visa_processed_logs
ORDER BY processed_at DESC
LIMIT 10;

-- Count processed emails
SELECT status, COUNT(*) as count
FROM st_visa_processed_logs
GROUP BY status;

-- Find failed processing
SELECT * FROM st_visa_processed_logs
WHERE status = 'failed'
ORDER BY processed_at DESC;
```

### View Extracted Visa Data

```sql
-- View recent visa documents
SELECT * FROM customer_documents
WHERE document_type = 'visa'
ORDER BY created_at DESC
LIMIT 10;

-- Find expiring visas
SELECT * FROM customer_documents
WHERE document_type = 'visa'
AND expiry_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 30 DAY)
ORDER BY expiry_date ASC;
```

## Troubleshooting

### Database Connection Issues

```bash
# Test database connection
python -c "from database import DatabaseManager; db = DatabaseManager(); print('✅ Connection OK')"

# Check if worker is running
kubectl get pods -l app=visa-reading-worker

# View logs
kubectl logs -l app=visa-reading-worker --tail=100 -f
```

### Worker Not Processing Emails

1. Check if worker is running: `kubectl get pods -l app=visa-reading-worker`
2. Check logs for errors: `kubectl logs -l app=visa-reading-worker --tail=100`
3. Verify environment variables: `kubectl describe pod <pod-name>`
4. Test Composio connection manually

### Worker Keeps Restarting

1. Check liveness probe: `kubectl describe pod <pod-name>`
2. Check resource limits: Worker may be OOM killed
3. Check database connectivity
4. Review logs before restart: `kubectl logs <pod-name> --previous`

### Graceful Shutdown Not Working

1. Check termination grace period: Should be 30 seconds
2. Verify signal handlers are registered
3. Check if current processing completes within grace period
4. Review logs during shutdown

### Database Connection Lost

The worker has auto-reconnect mechanism:
- Retries up to 3 times with exponential backoff
- Logs connection errors
- If all retries fail, the exception is raised and logged

## Migration from JSON to Database

The old `processed_emails.json` file is no longer used. To migrate existing data:

```python
import json
from database import DatabaseManager

db = DatabaseManager()

# Read old JSON file
with open('processed_emails.json') as f:
    old_data = json.load(f)

# Migrate to database
for email_id in old_data.get('processed_emails', []):
    db._log_failed_processing(
        email_id=email_id,
        passport_no=None,
        customer_name=None,
        error_message="Migrated from JSON"
    )
```

## Security Notes

- ✅ `.env` file is gitignored
- ✅ Kubernetes Secrets used for sensitive data
- ✅ Database credentials never hardcoded
- ⚠️ Rotate API keys regularly
- ⚠️ Use read-only database user if possible

## Performance

- **Processing time**: ~5-10 seconds per email
- **Batch size**: 50 emails per run (configurable)
- **Check interval**: 2 minutes (configurable)
- **Database queries**: Optimized with indexes

## Future Enhancements

- [ ] Customer ID auto-linking
- [ ] Email notification for expiring visas
- [ ] Webhook support for real-time processing
- [ ] Multi-language OCR support
- [ ] Retry mechanism for failed processing
- [ ] Metrics and alerting integration

## License

Internal use only - BANTU CRM
