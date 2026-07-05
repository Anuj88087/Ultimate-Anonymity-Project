#!/usr/bin/env python3
"""ANUJ — IP & MAC Rotator v2.0"""

import subprocess, random, time, sys, os, signal, shutil

# ─────────────────── CONFIG ───────────────────
INTERVAL    = 3
HISTORY_MAX = 15
# ──────────────────────────────────────────────

RED     = "\033[1;31m"
GREEN   = "\033[1;32m"
YELLOW  = "\033[1;33m"
CYAN    = "\033[1;36m"
WHITE   = "\033[1;37m"
DIM     = "\033[2m"
RESET   = "\033[0m"
CLEAR   = "\033[2J\033[H"
BOLD    = "\033[1m"

BANNER = f"""
{CYAN}   ░███    ░███    ░██ ░██     ░██     ░█████ 
  ░██░██   ░████   ░██ ░██     ░██       ░██  
 ░██  ░██  ░██░██  ░██ ░██     ░██       ░██  
░█████████ ░██ ░██ ░██ ░██     ░██       ░██  
░██    ░██ ░██  ░██░██ ░██     ░██ ░██   ░██  
░██    ░██ ░██   ░████  ░██   ░██  ░██   ░██  
░██    ░██ ░██    ░███   ░██████    ░██████   
                                             {RESET}
  {GREEN} Cyber Security Project —
                        {YELLOW} Created by ✤ ANUJ SRIVASTAVA
 ✤{RESET}
"""

history = []
cycle_count = 0
running = True


def shutdown(sig=None, frame=None):
    global running
    running = False
    print(f"\n\n  {RED}[✘] Shutdown signal received. Cleaning up...{RESET}")
    try:
        run(f"ip link set {IFACE} up")
    except:
        pass
    print(f"  {GREEN}[✔] Interface {IFACE} restored. Goodbye.{RESET}\n")
    sys.exit(0)


signal.signal(signal.SIGINT,  shutdown)
signal.signal(signal.SIGTERM, shutdown)


def run(cmd):
    try:
        result = subprocess.run(
            cmd, shell=True,
            capture_output=True, text=True, timeout=10
        )
        return result
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def get_interfaces():
    result = run("ls /sys/class/net")
    if result and result.stdout:
        ifaces = [i.strip() for i in result.stdout.split() if i.strip() != "lo"]
        return ifaces
    return []


def get_current_ip(iface):
    result = run(f"ip -4 addr show {iface}")
    if result and result.stdout:
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                return line.split()[1].split("/")[0]
    return None


def get_current_mac(iface):
    result = run(f"cat /sys/class/net/{iface}/address")
    if result and result.stdout:
        return result.stdout.strip()
    return None


def rand_mac():
    octets = [0x02] + [random.randint(0x00, 0xff) for _ in range(5)]
    return ":".join(f"{b:02x}" for b in octets)


def rand_ip():
    o2 = random.randint(0, 254)
    o3 = random.randint(0, 254)
    o4 = random.randint(1, 254)
    return f"10.{o2}.{o3}.{o4}"


def wait_for_ip(iface, retries=15):
    for _ in range(retries):
        ip = get_current_ip(iface)
        if ip:
            return ip
        time.sleep(0.3)
    return None


def wait_for_mac(iface, expected_mac, retries=10):
    for _ in range(retries):
        mac = get_current_mac(iface)
        if mac and mac.lower() == expected_mac.lower():
            return mac
        time.sleep(0.2)
    return get_current_mac(iface)


def draw_screen(iface, current_ip, current_mac, status, elapsed):
    cols = shutil.get_terminal_size().columns
    separator = f"  {DIM}{'─' * (cols - 4)}{RESET}"

    print(CLEAR, end="")
    print(BANNER)
    print(separator)
    print(f"  {WHITE}Interface  :{RESET}  {CYAN}{iface}{RESET}")
    print(f"  {WHITE}Current IP :{RESET}  {YELLOW}{current_ip or 'WAITING...'}{RESET}")
    print(f"  {WHITE}Current MAC:{RESET}  {CYAN}{current_mac or 'WAITING...'}{RESET}")
    print(f"  {WHITE}Cycle      :{RESET}  {GREEN}#{cycle_count}{RESET}")
    print(f"  {WHITE}Interval   :{RESET}  {DIM}{INTERVAL}s{RESET}")
    print(f"  {WHITE}Status     :{RESET}  {status}")
    print(f"  {WHITE}Uptime     :{RESET}  {DIM}{elapsed}{RESET}")
    print(separator)
    print(f"  {BOLD}{WHITE}   TIME        STATUS    MAC ADDRESS         IP ADDRESS{RESET}")
    print(separator)

    for entry in history[-HISTORY_MAX:]:
        print(f"  {entry}")

    print(separator)
    print(f"  {DIM}Ctrl+C to stop{RESET}")


def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def rotate(iface):
    global cycle_count

    new_mac = rand_mac()
    new_ip  = rand_ip()
    ts      = time.strftime('%H:%M:%S')

    # --- bring down ---
    res = run(f"ip link set {iface} down")
    if res is None or (res.returncode != 0):
        entry = f"  {DIM}{ts}{RESET}   {RED}[FAIL]{RESET}    interface down failed"
        history.append(entry)
        run(f"ip link set {iface} up")
        return None, None

    # --- set MAC ---
    run(f"ip link set {iface} address {new_mac}")

    # --- flush old IP, assign new ---
    run(f"ip addr flush dev {iface}")
    run(f"ip addr add {new_ip}/8 dev {iface}")

    # --- bring up ---
    run(f"ip link set {iface} up")

    # --- confirm ---
    confirmed_mac = wait_for_mac(iface, new_mac)
    confirmed_ip  = wait_for_ip(iface)

    cycle_count += 1

    if confirmed_ip and confirmed_mac:
        entry = (
            f"  {DIM}{ts}{RESET}   {GREEN}[ OK ]{RESET}    "
            f" {CYAN}{confirmed_mac}{RESET}   {YELLOW}{confirmed_ip}{RESET}"
        )
    elif confirmed_mac and not confirmed_ip:
        entry = (
            f"  {DIM}{ts}{RESET}   {YELLOW}[HALF]{RESET}    "
            f" {CYAN}{confirmed_mac}{RESET}   {RED}IP FAILED{RESET}"
        )
    else:
        entry = (
            f"  {DIM}{ts}{RESET}   {RED}[FAIL]{RESET}    "
            f" {RED}MAC FAILED{RESET}         {RED}IP FAILED{RESET}"
        )

    history.append(entry)
    return confirmed_ip, confirmed_mac


# ─────────────────── MAIN ───────────────────

def main():
    global IFACE

    if os.geteuid() != 0:
        print(f"\n  {RED}[✘] Root required. Run with: sudo python3 ghost.py{RESET}\n")
        sys.exit(1)

    # interface selection
    if len(sys.argv) > 1:
        IFACE = sys.argv[1]
    else:
        ifaces = get_interfaces()
        if not ifaces:
            print(f"\n  {RED}[✘] No network interfaces found.{RESET}\n")
            sys.exit(1)

        print(f"\n  {BOLD}Available interfaces:{RESET}\n")
        for i, iface in enumerate(ifaces):
            ip  = get_current_ip(iface)  or "no ip"
            mac = get_current_mac(iface) or "no mac"
            print(f"      {GREEN}[{i+1}]{RESET}  {CYAN}{iface:<15}{RESET}  {DIM}{mac}  |  {ip}{RESET}")

        print()
        try:
            choice = input(f"  {WHITE}Select interface [1-{len(ifaces)}]: {RESET}")
            idx = int(choice) - 1
            if idx < 0 or idx >= len(ifaces):
                raise ValueError
            IFACE = ifaces[idx]
        except (ValueError, EOFError):
            print(f"\n  {RED}[✘] Invalid selection.{RESET}\n")
            sys.exit(1)

    # verify interface exists
    if not os.path.exists(f"/sys/class/net/{IFACE}"):
        print(f"\n  {RED}[✘] Interface '{IFACE}' not found.{RESET}\n")
        sys.exit(1)

    start_time = time.time()

    print(CLEAR, end="")
    print(BANNER)
    print(f"\n  {GREEN}[✔] Starting rotation on {CYAN}{IFACE}{RESET}...\n")
    time.sleep(1)

    while running:
        try:
            status = f"{GREEN}● ROTATING{RESET}"
            elapsed = format_time(time.time() - start_time)

            current_ip, current_mac = rotate(IFACE)

            draw_screen(IFACE, current_ip, current_mac, status, elapsed)

            # sleep in small chunks so Ctrl+C responds fast
            for _ in range(INTERVAL * 10):
                if not running:
                    break
                time.sleep(0.1)

        except Exception as e:
            err_entry = f"  {DIM}{time.strftime('%H:%M:%S')}{RESET}   {RED}[ERR]{RESET}     {str(e)[:50]}"
            history.append(err_entry)

            # recovery — bring interface back up
            try:
                run(f"ip link set {IFACE} up")
            except:
                pass

            time.sleep(1)
            continue


if __name__ == "__main__":
    main()
    

