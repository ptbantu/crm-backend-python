#!/bin/bash
# APScheduler 签证预警系统 - 快速验证脚本

set -e

echo "=========================================="
echo "APScheduler 签证预警系统 - 快速验证"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. 检查文件是否存在
echo "1. 检查文件完整性..."
files=(
    "foundation_service/scheduler/__init__.py"
    "foundation_service/scheduler/visa_notification.py"
    "common/wecom_client.py"
    "init-scripts/migrations/add_visa_notification_field.sql"
    "k8s/deployments/wecom-secret.yaml"
    "docs/skills.md"
    "docs/DEPLOYMENT_VISA_NOTIFICATION.md"
    "test_visa_notification.py"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file"
    else
        check_fail "$file (缺失)"
    fi
done
echo ""

# 2. 检查依赖是否已添加
echo "2. 检查依赖配置..."
if grep -q "APScheduler" requirements.txt; then
    check_pass "APScheduler 已添加到 requirements.txt"
else
    check_fail "APScheduler 未添加到 requirements.txt"
fi

if grep -q "pytz" requirements.txt; then
    check_pass "pytz 已添加到 requirements.txt"
else
    check_fail "pytz 未添加到 requirements.txt"
fi
echo ""

# 3. 检查配置文件
echo "3. 检查配置文件..."
if grep -q "WECOM_WEBHOOK_URL" .env.example; then
    check_pass "企业微信配置已添加到 .env.example"
else
    check_fail "企业微信配置未添加到 .env.example"
fi

if grep -q "VISA_NOTIFICATION_ENABLED" .env.example; then
    check_pass "调度器配置已添加到 .env.example"
else
    check_fail "调度器配置未添加到 .env.example"
fi

if grep -q "Asia/Jakarta" .env.example; then
    check_pass "时区配置为 Asia/Jakarta"
else
    check_warn "时区可能未配置为 Asia/Jakarta"
fi
echo ""

# 4. 检查代码集成
echo "4. 检查代码集成..."
if grep -q "init_scheduler" foundation_service/main.py; then
    check_pass "调度器已集成到 main.py"
else
    check_fail "调度器未集成到 main.py"
fi

if grep -q "start_scheduler" foundation_service/main.py; then
    check_pass "调度器启动逻辑已添加"
else
    check_fail "调度器启动逻辑未添加"
fi

if grep -q "shutdown_scheduler" foundation_service/main.py; then
    check_pass "调度器关闭逻辑已添加"
else
    check_fail "调度器关闭逻辑未添加"
fi
echo ""

# 5. 检查配置类
echo "5. 检查配置类..."
if grep -q "WECOM_WEBHOOK_URL" common/config.py; then
    check_pass "企业微信配置已添加到 common/config.py"
else
    check_fail "企业微信配置未添加到 common/config.py"
fi

if grep -q "VISA_NOTIFICATION_ENABLED" common/config.py; then
    check_pass "调度器配置已添加到 common/config.py"
else
    check_fail "调度器配置未添加到 common/config.py"
fi
echo ""

# 6. 检查时区配置
echo "6. 检查时区配置..."
if grep -q "Asia/Jakarta" foundation_service/scheduler/__init__.py; then
    check_pass "调度器时区配置为 Asia/Jakarta"
else
    check_fail "调度器时区未配置为 Asia/Jakarta"
fi

if grep -q "JAKARTA_TZ" foundation_service/scheduler/visa_notification.py; then
    check_pass "签证预警任务使用雅加达时区"
else
    check_warn "签证预警任务可能未使用雅加达时区"
fi
echo ""

# 7. 检查数据库迁移脚本
echo "7. 检查数据库迁移脚本..."
if grep -q "last_notified_day" init-scripts/migrations/add_visa_notification_field.sql; then
    check_pass "数据库迁移脚本包含 last_notified_day 字段"
else
    check_fail "数据库迁移脚本缺少 last_notified_day 字段"
fi
echo ""

# 8. 检查 K8s Secret 配置
echo "8. 检查 K8s Secret 配置..."
if [ -f "k8s/deployments/wecom-secret.yaml" ]; then
    if grep -q "WECOM_WEBHOOK_URL" k8s/deployments/wecom-secret.yaml; then
        check_pass "K8s Secret 配置正确"
    else
        check_fail "K8s Secret 配置不完整"
    fi
else
    check_fail "K8s Secret 配置文件缺失"
fi
echo ""

# 9. 检查文档更新
echo "9. 检查文档更新..."
if grep -q "APScheduler" CLAUDE.md; then
    check_pass "CLAUDE.md 已更新"
else
    check_fail "CLAUDE.md 未更新"
fi

if [ -f "docs/skills.md" ]; then
    check_pass "docs/skills.md 已创建"
else
    check_fail "docs/skills.md 未创建"
fi
echo ""

# 10. Python 语法检查
echo "10. Python 语法检查..."
if command -v python3 &> /dev/null; then
    if python3 -m py_compile foundation_service/scheduler/__init__.py 2>/dev/null; then
        check_pass "scheduler/__init__.py 语法正确"
    else
        check_fail "scheduler/__init__.py 语法错误"
    fi

    if python3 -m py_compile foundation_service/scheduler/visa_notification.py 2>/dev/null; then
        check_pass "scheduler/visa_notification.py 语法正确"
    else
        check_fail "scheduler/visa_notification.py 语法错误"
    fi

    if python3 -m py_compile common/wecom_client.py 2>/dev/null; then
        check_pass "common/wecom_client.py 语法正确"
    else
        check_fail "common/wecom_client.py 语法错误"
    fi
else
    check_warn "Python3 未安装，跳过语法检查"
fi
echo ""

# 总结
echo "=========================================="
echo "验证完成"
echo "=========================================="
echo ""
echo "下一步操作："
echo "1. 安装依赖: pip install -r requirements.txt"
echo "2. 应用数据库迁移: kubectl exec -it <mysql-pod> -- mysql -u bantu_user -p bantu_crm < init-scripts/migrations/add_visa_notification_field.sql"
echo "3. 配置企业微信 Webhook: kubectl apply -f k8s/deployments/wecom-secret.yaml"
echo "4. 重启服务: kubectl rollout restart deployment/foundation-service"
echo "5. 查看日志: kubectl logs -l app=foundation-service --tail=100 -f"
echo "6. 运行测试: python test_visa_notification.py"
echo ""
