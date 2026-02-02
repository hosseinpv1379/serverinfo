# ServerInfo – مانیتورینگ سرعت شبکه سرورها

مانیتورینگ سرعت شبکه چند سرور به صورت هم‌زمان، مشابه خروجی **nload** اما به صورت عدد و از راه دور.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ویژگی‌ها

- **سرور**: سرویس سبک که سرعت ورودی/خروجی شبکه را به صورت API ارائه می‌دهد
- **کلاینت**: نمایش هم‌زمان سرعت چند سرور در یک جدول زنده
- **اسکریپت خودکار**: بدون نیاز به نصب دستی؛ فقط اجرا کن

## نصب سریع

```bash
git clone https://github.com/hosseinpv1379/serverinfo.git
cd serverinfo
```

### انتشار پروژه روی گیت‌هاب

```bash
./publish.sh
```

اگر مخزن وجود نداشته باشد، دستورالعمل نمایش داده می‌شود. با توکن:  
`export GITHUB_TOKEN=ghp_xxxx && ./publish.sh`

## استفاده

### سمت سرور

روی هر سروری که می‌خواهید سرعت شبکه‌اش را مانیتور کنید:

```bash
./server.sh
```

این اسکریپت خودکار:
- محیط مجازی پایتون می‌سازد
- وابستگی‌ها را نصب می‌کند
- سرور را روی پورت **8765** اجرا می‌کند

> پورت 8765 را در فایروال باز کنید تا از شبکه قابل دسترسی باشد.

### سمت کلاینت

روی ماشین خودتان:

```bash
# افزودن سرورها
./client.sh add http://192.168.1.10:8765
./client.sh add http://server2.example.com:8765

# شروع مانیتورینگ
./client.sh
```

یا مستقیم با آدرس سرورها:

```bash
./client.sh monitor http://192.168.1.10:8765 http://server2:8765
```

### دستورات کلاینت

| دستور | توضیح |
|-------|-------|
| `./client.sh` | مانیتورینگ (پیش‌فرض) |
| `./client.sh add <url>` | افزودن سرور |
| `./client.sh list` | لیست سرورهای ذخیره شده |
| `./client.sh remove <url یا شماره>` | حذف سرور |
| `./client.sh monitor [url1] [url2] ...` | مانیتور با آدرس مستقیم |

## لینک‌ها

**مخزن گیت:**
```
https://github.com/hosseinpv1379/serverinfo
```

**اسکریپت سرور (raw):**
```
https://raw.githubusercontent.com/hosseinpv1379/serverinfo/main/server.sh
```

**اسکریپت کلاینت (raw):**
```
https://raw.githubusercontent.com/hosseinpv1379/serverinfo/main/client.sh
```

**کلون و اجرا:**
```bash
git clone https://github.com/hosseinpv1379/serverinfo.git && cd serverinfo
./server.sh   # روی سرور
./client.sh   # روی کلاینت
```

## API سرور

| Endpoint | خروجی |
|----------|-------|
| `GET /speed` | `{"incoming": X, "outgoing": Y, "unit": "B/s"}` |
| `GET /speed/kb` | سرعت به کیلوبایت/ثانیه |
| `GET /speed/mb` | سرعت به مگابایت/ثانیه |

## پیش‌نیازها

- Python 3.9+
- دسترسی شبکه به پورت 8765 روی سرورها

## مجوز

MIT
