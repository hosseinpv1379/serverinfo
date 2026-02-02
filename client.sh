#!/bin/bash
# اسکریپت خودکار کلاینت - نصب و اجرا
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/.venv-client"

# بررسی پایتون
if ! command -v python3 &>/dev/null; then
    echo "خطا: پایتون 3 یافت نشد. لطفاً نصب کنید."
    exit 1
fi

# ساخت venv در صورت نبود
if [ ! -d "$VENV_DIR" ]; then
    echo "در حال ساخت محیط مجازی..."
    python3 -m venv "$VENV_DIR"
fi

# فعال‌سازی و نصب
echo "در حال نصب وابستگی‌ها..."
"$VENV_DIR/bin/pip" install -q --upgrade pip
"$VENV_DIR/bin/pip" install -q httpx rich

# اجرا با آرگومان‌های دریافتی
exec "$VENV_DIR/bin/python" client.py "$@"
