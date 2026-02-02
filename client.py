#!/usr/bin/env python3
"""
کلاینت مانیتورینگ سرعت شبکه
اتصال به چند سرور و نمایش سرعت هر کدام
"""

import argparse
import asyncio
import sys
from pathlib import Path

import httpx
from rich.console import Console
from rich.live import Live
from rich.table import Table


CONFIG_FILE = Path.home() / ".config" / "serverinfo" / "servers.txt"
DEFAULT_SERVERS = [
    "http://localhost:8765",
]


def load_servers_from_config() -> list[str]:
    """خواندن لیست سرورها از فایل کانفیگ"""
    if CONFIG_FILE.exists():
        lines = CONFIG_FILE.read_text().strip().splitlines()
        return [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    return []


def save_servers_to_config(servers: list[str]) -> None:
    """ذخیره لیست سرورها در فایل کانفیگ"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text("\n".join(servers))


def format_speed(bps: float) -> str:
    """فرمت خوانا برای سرعت"""
    if bps is None or bps < 0:
        return "N/A"
    if bps >= 1024 * 1024 * 1024:
        return f"{bps / (1024**3):.2f} GB/s"
    if bps >= 1024 * 1024:
        return f"{bps / (1024**2):.2f} MB/s"
    if bps >= 1024:
        return f"{bps / 1024:.2f} KB/s"
    return f"{bps:.1f} B/s"


async def fetch_speed(client: httpx.AsyncClient, url: str, unit: str = "B/s") -> dict | None:
    """دریافت سرعت از یک سرور"""
    try:
        endpoint = "/speed" if unit == "B/s" else f"/speed/{unit.lower().replace('/s', '')}"
        r = await client.get(f"{url.rstrip('/')}{endpoint}", timeout=2.0)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def create_table(servers_data: dict) -> Table:
    """ساخت جدول نمایش"""
    table = Table(
        title="سرعت شبکه سرورها (مشابه nload)",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("سرور", style="dim")
    table.add_column("ورودی (In)", justify="right", style="green")
    table.add_column("خروجی (Out)", justify="right", style="yellow")

    for url, data in servers_data.items():
        if data is None:
            table.add_row(url, "[red]قطع[/red]", "[red]قطع[/red]")
        else:
            inc = data.get("incoming", 0)
            out = data.get("outgoing", 0)
            unit = data.get("unit", "B/s")
            if unit == "KB/s":
                inc, out = inc * 1024, out * 1024
            elif unit == "MB/s":
                inc, out = inc * 1024 * 1024, out * 1024 * 1024
            table.add_row(
                url,
                format_speed(inc),
                format_speed(out),
            )

    return table


async def monitor_loop(servers: list[str], interval: float = 1.0):
    """حلقه اصلی مانیتورینگ"""
    console = Console()
    servers_data = {s: None for s in servers}

    async with httpx.AsyncClient() as client:
        with Live(
            create_table(servers_data),
            refresh_per_second=2,
            console=console,
        ) as live:
            while True:
                tasks = [fetch_speed(client, s) for s in servers]
                results = await asyncio.gather(*tasks)
                servers_data = dict(zip(servers, results))
                live.update(create_table(servers_data))
                await asyncio.sleep(interval)


def cmd_list(servers: list[str]):
    """لیست سرورهای ذخیره شده"""
    if not servers:
        print("هیچ سروری ذخیره نشده.")
        print("استفاده: serverinfo-client add <url>")
        return
    for i, s in enumerate(servers, 1):
        print(f"  {i}. {s}")


def cmd_add(servers: list[str], url: str):
    """افزودن سرور"""
    url = url.rstrip("/")
    if url in servers:
        print(f"سرور {url} از قبل وجود دارد.")
        return
    servers.append(url)
    save_servers_to_config(servers)
    print(f"سرور اضافه شد: {url}")


def cmd_remove(servers: list[str], url_or_index: str):
    """حذف سرور"""
    url_or_index = url_or_index.strip()
    if url_or_index.isdigit():
        idx = int(url_or_index) - 1
        if 0 <= idx < len(servers):
            removed = servers.pop(idx)
            save_servers_to_config(servers)
            print(f"سرور حذف شد: {removed}")
            return
    if url_or_index in servers:
        servers.remove(url_or_index)
        save_servers_to_config(servers)
        print(f"سرور حذف شد: {url_or_index}")
        return
    print("سرور یافت نشد.")


def main():
    parser = argparse.ArgumentParser(
        prog="serverinfo-client",
        description="کلاینت مانیتورینگ سرعت شبکه - اتصال به چند سرور",
    )
    sub = parser.add_subparsers(dest="cmd", help="دستور")

    # دستور پیش‌فرض: مانیتور
    monitor_p = sub.add_parser("monitor", help="شروع مانیتورینگ (پیش‌فرض)")
    monitor_p.set_defaults(cmd="monitor")
    monitor_p.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="فاصله بروزرسانی (ثانیه)",
    )
    monitor_p.add_argument(
        "servers",
        nargs="*",
        help="آدرس سرورها (در صورت نبود از کانفیگ خوانده می‌شود)",
    )

    # لیست سرورها
    sub.add_parser("list", help="لیست سرورهای ذخیره شده")

    # افزودن سرور
    add_p = sub.add_parser("add", help="افزودن سرور")
    add_p.add_argument("url", help="آدرس سرور (مثال: http://192.168.1.10:8765)")

    # حذف سرور
    rm_p = sub.add_parser("remove", help="حذف سرور")
    rm_p.add_argument("url_or_index", help="آدرس یا شماره سرور")

    args = parser.parse_args()
    servers = load_servers_from_config() or DEFAULT_SERVERS.copy()

    # اگر زیردستور نداد، monitor فرض می‌شود
    if args.cmd is None:
        args.cmd = "monitor"
        args.servers = []
        args.interval = 1.0

    if args.cmd == "list":
        cmd_list(servers)
        return

    if args.cmd == "add":
        cmd_add(servers, args.url)
        return

    if args.cmd == "remove":
        cmd_remove(servers, args.url_or_index)
        return

    # monitor
    monitor_servers = getattr(args, "servers", [])
    if monitor_servers:
        servers = [s if s.startswith("http") else f"http://{s}" for s in monitor_servers]
    elif not servers:
        print("هیچ سروری تنظیم نشده. استفاده:")
        print("  serverinfo-client add http://IP:8765")
        print("  serverinfo-client monitor")
        sys.exit(1)

    try:
        asyncio.run(monitor_loop(servers, getattr(args, "interval", 1.0)))
    except KeyboardInterrupt:
        print("\nخروج.")


if __name__ == "__main__":
    main()
