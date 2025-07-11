#!/usr/bin/env python3

from scapy.all import sniff, IP, TCP, UDP, get_if_list, wrpcap
from colorama import Fore, Style, init
import argparse
import datetime
import sys

init(autoreset=True)

def banner():
    print(rf"""{Fore.CYAN}
   _____       _  __ _           
  / ____|     (_)/ _(_)          
 | (___  _ __  _| |_ _  ___ _ __ 
  \___ \| '_ \| |  _| |/ _ \ '__|
  ____) | | | | | | | |  __/ |   
 |_____/|_| |_|_|_| |_|\___|_|   
{Style.RESET_ALL}{Fore.MAGENTA}
     Created by Salik Seraj Naik ✨
     Simple CLI Packet Sniffer Tool
{Style.RESET_ALL}
""")

def validate_interface(interface):
    interfaces = get_if_list()
    if interface not in interfaces:
        print(f"{Fore.RED}[!] Interface '{interface}' not found!{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}[*] Available interfaces:{Style.RESET_ALL}")
        for iface in interfaces:
            print(f"   ➤ {iface}")
        sys.exit(1)

def packet_callback(packet):
    if IP in packet:
        ip_layer = packet[IP]
        proto = "OTHER"

        if packet.haslayer(TCP):
            proto = "TCP"
        elif packet.haslayer(UDP):
            proto = "UDP"

        print(f"{Fore.YELLOW}[{datetime.datetime.now().strftime('%H:%M:%S')}] "
              f"{Fore.BLUE}{ip_layer.src} {Style.RESET_ALL}-> "
              f"{Fore.RED}{ip_layer.dst} {Style.RESET_ALL}| "
              f"{Fore.GREEN}{proto}{Style.RESET_ALL}")

        if args.payload and (packet.haslayer(TCP) or packet.haslayer(UDP)):
            payload = bytes(packet[TCP].payload)[:40]
            if payload:
                print(f"{Fore.MAGENTA}    Payload: {payload!r}{Style.RESET_ALL}")

        if args.log:
            with open(args.log, "a") as logf:
                logf.write(f"{ip_layer.src} -> {ip_layer.dst} | Protocol: {proto}\n")

def save_pcap(packets):
    filename = f"capture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pcap"
    wrpcap(filename, packets)
    print(f"\n{Fore.GREEN}[✓] Saved captured packets to: {filename}{Style.RESET_ALL}")

def main():
    banner()
    validate_interface(args.interface)
    print(f"{Fore.CYAN}[*] Starting capture on interface: {args.interface}{Style.RESET_ALL}\n")

    try:
        packets = sniff(prn=packet_callback, iface=args.interface, filter=args.filter, store=True)
    except PermissionError:
        print(f"{Fore.RED}[!] Run this script with sudo or as administrator.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    # Save .pcap when sniffing ends (e.g. Ctrl+C)
    save_pcap(packets)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cool Python Packet Sniffer by Salik Seraj Naik")
    parser.add_argument("-i", "--interface", required=True, help="Interface to sniff on (e.g., eth0, wlan0, lo)")
    parser.add_argument("-f", "--filter", default="", help="BPF filter (e.g., tcp, udp, port 80)")
    parser.add_argument("-p", "--payload", action="store_true", help="Print packet payloads")
    parser.add_argument("-l", "--log", help="Path to log file (optional)")

    args = parser.parse_args()
    main()
