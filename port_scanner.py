#!/usr/bin/env python3
"""Multi-threaded TCP port scanner.

Features:
- Fast scanning using ThreadPoolExecutor.
- Configurable host, port list/range, timeout, and worker count.
- Graceful handling of Ctrl+C (KeyboardInterrupt).
- Clean terminal output with an ASCII banner and a summary report.

Only Python standard library modules are used, so it runs on any modern Python 3 installation.
"""

import argparse
import socket
import concurrent.futures
import time
import sys
import threading

# ANSI colour codes (will be ignored if the terminal does not support them)
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BANNER = rf"""
{YELLOW}  ____            _   _                 _   
{YELLOW} |  _ \ ___  __ _| |_| |__   ___   ___ | |_ 
{YELLOW} | |_) / _ \/ _` | __| '_ \ / _ \ / _ \| __|
{YELLOW} |  __/  __/ (_| | |_| | | | (_) | (_) | |_ 
{YELLOW} |_|   \___|\__,_|\__|_| |_|\___/ \___/ \__|
{YELLOW}                                            
{RESET}"""

def parse_ports(port_str: str) -> list[int]:
    """Parse a comma‑separated list of ports and ranges.

    Examples
    --------
    "80,443,8000-8010" -> [80, 443, 8000, 8001, ..., 8010]
    """
    ports = set()
    for part in port_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ports.update(range(int(start), int(end) + 1))
        elif part:
            ports.add(int(part))
    return sorted(ports)

def scan_port(host: str, port: int, timeout: float) -> bool:
    """Try to open a TCP connection to *host*: *port*.

    Returns ``True`` if the port is open, ``False`` otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except socket.error:
            return False

def human_readable_duration(seconds: float) -> str:
    """Convert a duration in seconds to a human readable string."""
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    if hrs:
        return f"{int(hrs)}h {int(mins)}m {secs:.2f}s"
    elif mins:
        return f"{int(mins)}m {secs:.2f}s"
    else:
        return f"{secs:.2f}s"

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fast multi‑threaded TCP port scanner",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("host", help="Target host or IP address")
    parser.add_argument(
        "-p",
        "--ports",
        default="",
        help="Comma separated ports and ranges (e.g. 80,443,8000-8010). "
        "If omitted, a built‑in list of common ports is used.",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=0.5,
        help="Connection timeout in seconds (default: 0.5)",
    )
    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=100,
        help="Maximum number of concurrent threads (default: 100)",
    )

    args = parser.parse_args()

    # Default list of frequently used ports if the user didn't supply any.
    default_common_ports = [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
        1723, 3306, 3389, 5900, 8080, 8443, 10000,
    ]

    ports = (
        parse_ports(args.ports) if args.ports else default_common_ports
    )

    print(BANNER)
    print(f"Scanning {args.host} for {len(ports)} ports (timeout={args.timeout}s)…\n")

    start_time = time.time()
    open_ports = []
    lock = threading.Lock()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_to_port = {
                executor.submit(scan_port, args.host, port, args.timeout): port
                for port in ports
            }
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    is_open = future.result()
                except Exception:
                    is_open = False
                with lock:
                    if is_open:
                        open_ports.append(port)
                        print(f"{GREEN}[OPEN]   Port {port}{RESET}")
                    else:
                        print(f"{RED}[CLOSED] Port {port}{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Interrupted by user – shutting down gracefully...{RESET}")
        sys.exit(0)

    duration = time.time() - start_time
    print("\n" + "=" * 60)
    print(f"Scan completed in {human_readable_duration(duration)}")
    print(f"Total ports scanned : {len(ports)}")
    print(f"Open ports          : {len(open_ports)}")
    if open_ports:
        print("Open ports list    : " + ", ".join(map(str, open_ports)))
    print("=" * 60)

if __name__ == "__main__":
    main()