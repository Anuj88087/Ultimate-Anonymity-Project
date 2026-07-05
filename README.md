# Ultimate Anonymity: Automated Network Identity & Tor Rotator

Ultimate Anonymity is a lightweight Python automation tool built for network privacy research, pentesting, and defensive OpSec auditing. It helps you manage and mask your network-layer identifiers (like MAC and IP addresses) automatically in Linux setups, without any manual hassle.

---

## 🛠️ How It Works (Project Architecture)

The script works at both the hardware and network routing levels to obscure your footprint and minimize mass tracking:

### 1. Smart Interface Detection
- As soon as you run the script, it scans your system's routing table to automatically find your active network gateway (whether it is `wlan0`, `eth0`, or `wlp3s0`). This completely eliminates manual configuration errors.

### 2. On-Demand MAC Address Spoofing
- Once the active interface is found, the script safely brings the interface down, triggers `macchanger` to assign a completely random MAC address, and brings it back up. This prevents local Wi-Fi routers or network admins from tracking your physical machine.

### 3. Rate-Limit Compliant Tor Rotation
- The script opens a raw authenticated socket connection to the Tor Control Port (Port 9051).
- During each loop, it safely requests a fresh circuit path by sending a `SIGNAL NEWNYM` command.
- To avoid circuit drops and respect Tor’s built-in rate limits, a **15-second delay** is enforced, keeping your public Exit IP rotating safely and continuously.

### 4. Continuous Routing Verification
- It uses the `torsocks` wrapper to securely query public IP checkers and logs your active exit node IP to the console in real-time, confirming that your traffic is properly masked.

---

## 🎯 Use Cases

1. **Penetration Testing & Bug Hunting:** Avoid hitting strict rate limits or getting your real IP blocked by targets while running authorized security audits or web scraping tasks.
2. **OpSec & Surveillance Analysis:** Test and study how modern network tracking mechanisms analyze multi-layered web traffic.
3. **Local Privacy Enforcement:** Protect your machine's hardware identity from being permanently logged into public or corporate Wi-Fi access points.

---

## 🚀 Setup & Installation

### 1. Install Dependencies
First, make sure you have Tor, macchanger, and netcat installed on your Linux machine:
```bash
sudo apt update && sudo apt install tor macchanger netcat-openbsd -y
```
2. Configure Tor Control Port
To let the Python script talk to Tor, you need to open its control port. Open the configuration file:
sudo nano /etc/tor/torrc
Look for these lines, uncomment them (remove the #), or simply paste them at the bottom of the file:
ControlPort 9051
CookieAuthentication 0
Save the file (Ctrl+O, then Enter, then Ctrl+X) and restart your Tor service:
```bash
sudo systemctl restart tor
```
4. Run the Script
Now give execution permissions to the script and run it as root:
chmod +x ultimate_anonymity.py
sudo python3 ultimate_anonymity.py

Disclaimer: This project is strictly for educational research and authorized security assessments. Please use it responsibly.
```bash
sudo python3 ghost.py
```

