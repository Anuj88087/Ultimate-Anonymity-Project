#!/usr/bin/env python3
import subprocess
import time
import os
import sys

TOR_PASSWORD = "test123" 

class UltimateAnonymityFixed:
    def __init__(self):
        self.ip_count = 0
        self.mac_count = 0
        self.interface = self.get_active_interface()

    def get_active_interface(self):
        try:
            route_output = subprocess.check_output(["ip", "route", "show", "default"], text=True)
            for word in route_output.split():
                if word in ['dev']:
                    idx = route_output.split().index(word)
                    return route_output.split()[idx+1]
        except Exception:
            return None
        return None

    def change_mac(self):
        if not self.interface:
            print("[!] Active interface nahi mila. MAC spoofing skipped.")
            return
        
        print(f"[*] Changing MAC address for interface: {self.interface}")
        subprocess.run(["sudo", "ip", "link", "set", self.interface, "down"], capture_output=True)
        subprocess.run(["sudo", "macchanger", "-r", self.interface], capture_output=True)
        subprocess.run(["sudo", "ip", "link", "set", self.interface, "up"], capture_output=True)
        self.mac_count += 1
        time.sleep(3)

    def change_tor_ip(self):
        cmd = f'echo -e "AUTHENTICATE \"{TOR_PASSWORD}\"\r\nSIGNAL NEWNYM\r\nQUIT" | nc 127.0.0.1 9051'
        subprocess.run(cmd, shell=True, capture_output=True)
        self.ip_count += 1

    def get_current_ip(self):
        try:
            r = subprocess.run(["torsocks", "curl", "-s", "--max-time", "5", "https://icanhazip.com"], 
                               capture_output=True, text=True)
            return r.stdout.strip()
        except Exception:
            return "Circuit Building / Request Timeout"

    def run(self):
        os.system("clear")
        print("="*60)
        print("        FIXED ULTIMATE ANONYMITY LAYER MANAGER")
        print("="*60)
        
        if not self.interface:
            print("[-] Error: Koi active gateway interface nahi mila. Check network connection.")
            sys.exit(1)
            
        print(f"[✓] Active Interface Detected: {self.interface}")
        
        self.change_mac()
        print("[*] Ensuring Tor service is active...")
        subprocess.run(["sudo", "systemctl", "start", "tor"])
        time.sleep(2)
        
        print("\n[✓] Rotation Loop Active. Press Ctrl+C to safely exit.\n")
        
        try:
            while True:
                self.change_tor_ip()
                time.sleep(2) 
                
                current_ip = self.get_current_ip()
                print(f"[{self.ip_count}] [{time.strftime('%H:%M:%S')}] Active Exit IP: {current_ip}")
                
                if self.ip_count % 20 == 0:
                    print("\n[*] Periodic identity refresh initiated...")
                    self.change_mac()
                
                time.sleep(13)
                
        except KeyboardInterrupt:
            print(f"\n\n[!] Script stopped by user.")
            print(f" -> Total Tor IP Changes: {self.ip_count}")
            print(f" -> Total MAC Spoofs: {self.mac_count}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("[-] Please run this script with root privileges: sudo python3 ultimate_anonymity_fixed.py")
        sys.exit(1)
    UltimateAnonymityFixed().run()
