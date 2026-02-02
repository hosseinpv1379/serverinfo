#!/bin/bash
# اسکریپت انتشار روی گیت‌هاب
set -e

REPO_NAME="serverinfo"
USERNAME="hosseinpv1379"
REMOTE="https://github.com/${USERNAME}/${REPO_NAME}.git"

cd "$(dirname "${BASH_SOURCE[0]}")"

# بررسی وجود مخزن
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://api.github.com/repos/${USERNAME}/${REPO_NAME}" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "404" ] || [ "$HTTP_CODE" = "000" ]; then
    echo "مخزن ${REPO_NAME} روی گیت‌هاب وجود نداره."

    if [ -n "$GITHUB_TOKEN" ]; then
        echo "در حال ساخت مخزن با API..."
        if curl -s -X POST -H "Authorization: token ${GITHUB_TOKEN}" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/user/repos" \
            -d "{\"name\":\"${REPO_NAME}\",\"description\":\"Network speed monitoring - nload style\",\"private\":false}" \
            > /dev/null 2>&1; then
            echo "مخزن ساخته شد."
        else
            echo "خطا در ساخت مخزن. توکن را بررسی کن."
            exit 1
        fi
    else
        echo ""
        echo "یکی از این روش‌ها را انجام بده:"
        echo ""
        echo "۱) ساخت دستی:"
        echo "   https://github.com/new?name=${REPO_NAME}"
        echo "   Create repository بزن (بدون README)"
        echo ""
        echo "۲) با توکن: export GITHUB_TOKEN=ghp_xxxx && ./publish.sh"
        echo "۳) با gh: gh repo create ${REPO_NAME} --public --source=. --push"
        exit 1
    fi
fi

# اطمینان از remote
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"

# پوش
echo "در حال ارسال به گیت‌هاب..."
git push -u origin main
git push origin main:master 2>/dev/null || true  # همگام‌سازی master برای سازگاری

echo "✅ انجام شد: https://github.com/${USERNAME}/${REPO_NAME}"
