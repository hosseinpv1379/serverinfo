#!/usr/bin/env python3
"""
سرور مانیتورینگ سرعت شبکه
خروجی مشابه nload: سرعت دانلود و آپلود به صورت عدد
"""

import time
import asyncio
from contextlib import asynccontextmanager

import psutil
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ذخیره آخرین نمونه برای محاسبه سرعت
_last_sample = {"bytes_sent": 0, "bytes_recv": 0, "time": 0}


def get_network_speed():
    """محاسبه سرعت شبکه بر اساس نمونه‌گیری (bytes/sec)"""
    global _last_sample
    counters = psutil.net_io_counters()
    now = time.time()

    bytes_sent = counters.bytes_sent
    bytes_recv = counters.bytes_recv

    if _last_sample["time"] == 0:
        _last_sample = {
            "bytes_sent": bytes_sent,
            "bytes_recv": bytes_recv,
            "time": now,
        }
        return {"incoming": 0, "outgoing": 0, "unit": "B/s"}

    elapsed = now - _last_sample["time"]
    if elapsed < 0.1:  # حداقل فاصله برای دقت
        elapsed = 0.1

    incoming = (bytes_recv - _last_sample["bytes_recv"]) / elapsed
    outgoing = (bytes_sent - _last_sample["bytes_sent"]) / elapsed

    _last_sample = {
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
        "time": now,
    }

    return {
        "incoming": round(incoming, 2),
        "outgoing": round(outgoing, 2),
        "unit": "B/s",
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    """آماده‌سازی اولیه"""
    get_network_speed()  # نمونه اول برای شروع
    yield


app = FastAPI(
    title="Network Speed Server",
    description="API سرعت شبکه مشابه nload",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"status": "ok", "message": "Network Speed Server - استفاده: GET /speed"}


@app.get("/speed")
async def speed():
    """برگرداندن سرعت فعلی شبکه (ورودی و خروجی) به بایت بر ثانیه"""
    return get_network_speed()


@app.get("/speed/kb")
async def speed_kb():
    """سرعت به کیلوبایت بر ثانیه"""
    s = get_network_speed()
    return {
        "incoming": round(s["incoming"] / 1024, 2),
        "outgoing": round(s["outgoing"] / 1024, 2),
        "unit": "KB/s",
    }


@app.get("/speed/mb")
async def speed_mb():
    """سرعت به مگابایت بر ثانیه"""
    s = get_network_speed()
    return {
        "incoming": round(s["incoming"] / (1024 * 1024), 2),
        "outgoing": round(s["outgoing"] / (1024 * 1024), 2),
        "unit": "MB/s",
    }


def format_speed(bps):
    """فرمت خوانا برای سرعت"""
    if bps >= 1024 * 1024:
        return f"{bps / (1024*1024):.2f} MB/s"
    if bps >= 1024:
        return f"{bps / 1024:.2f} KB/s"
    return f"{bps:.1f} B/s"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="سرور سرعت شبکه")
    parser.add_argument("--host", default="0.0.0.0", help="آدرس میزبان")
    parser.add_argument("--port", type=int, default=8765, help="پورت")
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
