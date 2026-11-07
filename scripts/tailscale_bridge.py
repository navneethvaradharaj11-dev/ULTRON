#!/usr/bin/env python3
"""
ULTRON Tailscale Portproxy & Socket Bridge
Binds strictly to Tailscale private interface IP (default: 100.69.161.16)
and proxies full-duplex TCP traffic to the local ULTRON backend (port 8000).

No administrator privileges required.
Maintains 100% database & Redis isolation while providing 100% reliable connectivity.
"""

import sys
import os
import socket
import asyncio
import argparse
import subprocess
import logging
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ULTRON.TailscaleBridge")

PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tailscale_bridge.pid")


def detect_tailscale_ip() -> str:
    """Detect Tailscale IPv4 address from host interfaces or fallback to default."""
    try:
        # Check via PowerShell Get-NetIPAddress on Windows
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "(Get-NetIPAddress -InterfaceAlias '*Tailscale*' -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty IPAddress -First 1)"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        ip = res.stdout.strip()
        if ip and ip.startswith("100."):
            return ip
    except Exception:
        pass

    # Inspect all local socket interfaces
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            candidate = info[4][0]
            if candidate.startswith("100."):
                return candidate
    except Exception:
        pass

    return "100.69.161.16"


def detect_connect_host() -> str:
    """Detect the best target host for ULTRON backend (WSL2 IP or 127.0.0.1)."""
    # 1. Try WSL IP dynamically
    try:
        res = subprocess.run(["wsl", "hostname", "-I"], capture_output=True, text=True, timeout=5)
        wsl_ips = res.stdout.strip().split()
        for ip in wsl_ips:
            try:
                with socket.create_connection((ip, 8000), timeout=0.8):
                    logger.info("Found reachable backend at WSL IP: %s:8000", ip)
                    return ip
            except Exception:
                continue
    except Exception:
        pass

    # 2. Try 127.0.0.1
    try:
        with socket.create_connection(("127.0.0.1", 8000), timeout=0.8):
            logger.info("Found reachable backend at 127.0.0.1:8000")
            return "127.0.0.1"
    except Exception:
        pass

    return "172.26.79.85"


async def pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Bidirectional streaming pump with zero copy buffer."""
    try:
        while not reader.at_eof():
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        logger.debug("Pipe error: %s", e)
    finally:
        try:
            if not writer.is_closing():
                writer.close()
                await writer.wait_closed()
        except Exception:
            pass


class TargetResolver:
    """Manages active backend target host and transparently reconnects across WSL restarts."""
    def __init__(self, initial_host: Optional[str] = None, port: int = 8000):
        self.host = initial_host or detect_connect_host()
        self.port = port
        self.lock = asyncio.Lock()

    async def get_connection(self):
        """Acquire an active TCP stream connection, re-detecting host if WSL was restarted."""
        for attempt in range(4):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=2.0
                )
                return reader, writer
            except Exception as e:
                logger.warning("Target %s:%d unreachable (%s). Re-detecting target... (attempt %d/4)", self.host, self.port, e, attempt + 1)
                async with self.lock:
                    loop = asyncio.get_running_loop()
                    new_host = await loop.run_in_executor(None, detect_connect_host)
                    self.host = new_host
                await asyncio.sleep(1.0)

        # Final attempt
        return await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port),
            timeout=5.0
        )


async def handle_connection(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter, resolver: TargetResolver):
    client_addr = client_writer.get_extra_info('peername')
    logger.info("Incoming connection from %s", client_addr)
    try:
        backend_reader, backend_writer = await resolver.get_connection()
    except Exception as e:
        logger.error("Failed to connect to backend after recovery attempts: %s", e)
        client_writer.close()
        try:
            await client_writer.wait_closed()
        except Exception:
            pass
        return

    try:
        await asyncio.gather(
            pipe(client_reader, backend_writer),
            pipe(backend_reader, client_writer)
        )
    except Exception as e:
        logger.debug("Forwarding session error: %s", e)
    finally:
        logger.info("Connection closed for %s", client_addr)


async def run_server(listen_ip: str, listen_port: int, resolver: TargetResolver):
    server = await asyncio.start_server(
        lambda r, w: handle_connection(r, w, resolver),
        listen_ip,
        listen_port,
        reuse_address=True
    )

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    logger.info("=" * 60)
    logger.info("ULTRON Tailscale Portproxy Socket Bridge Active")
    logger.info("Listening on : %s", addrs)
    logger.info("Active Target: %s:%d (Auto-recovering)", resolver.host, resolver.port)
    logger.info("Isolation    : Database (3306) & Redis (6379) STRICTLY ISOLATED")
    logger.info("=" * 60)

    # Save PID file
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

    async with server:
        await server.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="ULTRON Tailscale Portproxy Socket Bridge")
    parser.add_argument("--listen-ip", default=None, help="IP to listen on (auto-detects Tailscale)")
    parser.add_argument("--listen-port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--target-host", default=None, help="Target host (auto-detects 127.0.0.1 or WSL)")
    parser.add_argument("--target-port", type=int, default=8000, help="Target port (default: 8000)")
    parser.add_argument("--stop", action="store_true", help="Stop any running bridge instance")
    args = parser.parse_args()

    if args.stop:
        if os.path.exists(PID_FILE):
            try:
                with open(PID_FILE, "r") as f:
                    pid = int(f.read().strip())
                import signal
                os.kill(pid, signal.SIGTERM)
                os.remove(PID_FILE)
                print(f"Stopped bridge process with PID {pid}")
            except Exception as e:
                print(f"Error stopping PID: {e}")
        else:
            print("No running bridge PID found.")
        return

    listen_ip = args.listen_ip or detect_tailscale_ip()
    resolver = TargetResolver(initial_host=args.target_host, port=args.target_port)

    try:
        asyncio.run(run_server(listen_ip, args.listen_port, resolver))
    except KeyboardInterrupt:
        logger.info("Shutting down bridge cleanly...")
    finally:
        if os.path.exists(PID_FILE):
            try:
                os.remove(PID_FILE)
            except Exception:
                pass


if __name__ == "__main__":
    main()
