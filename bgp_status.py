import requests
import urllib3
import argparse
import csv
from getpass import getpass
from tabulate import tabulate

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === Argument Parsing ===
parser = argparse.ArgumentParser(description="Fetch BGP neighbors from vManage and output to table or CSV")
parser.add_argument("-o", "--output", help="Optional: Output CSV filename (e.g. neighbors.csv)")
args = parser.parse_args()

# === Configuration ===
# Hardcoded vManage connection details
vman_host_ip = "vmanage.cisco.com"
vman_port = "8443"
username = "yourusername"
password = "yourpassword"

# === Prompt for device IDs ===
device_ids_input = input("Enter deviceId(s), comma-separated: ")
device_ids = [d.strip() for d in device_ids_input.split(",") if d.strip()]

# === Authenticate Session ===
session = requests.session()
login_url = f"https://{vman_host_ip}:{vman_port}/j_security_check"
token_url = f"https://{vman_host_ip}:{vman_port}/dataservice/client/token"

payload = {'j_username': username, 'j_password': password}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = session.post(url=login_url, data=payload, headers=headers, verify=False)
if response.status_code != 200 or 'html' in response.text.lower():
    print("❌ Login failed.")
    exit()

token_response = session.get(url=token_url, verify=False)
if token_response.status_code == 200:
    token = token_response.text
    session.headers['X-XSRF-TOKEN'] = token
else:
    print("❌ Token fetch failed.")
    exit()

# === Collect BGP neighbor data ===
headers_row = ["Hostname", "VPN-ID", "Remote ASN", "Peer IP", "State"]
table_rows = []

for device_id in device_ids:
    print(f"\n🔍 Fetching BGP neighbors for deviceId: {device_id}")
    bgp_url = f"https://{vman_host_ip}:{vman_port}/dataservice/device/bgp/neighbors?deviceId={device_id}"
    response = session.get(url=bgp_url, verify=False)

    if response.status_code != 200:
        print(f"❌ Failed to fetch BGP neighbors for {device_id}")
        continue

    bgp_data = response.json().get("data", [])

    for neighbor in bgp_data:
        hostname = neighbor.get("vdevice-host-name", "N/A")
        vpn_id = neighbor.get("vpn-id", "0")
        asn = neighbor.get("as", "N/A")
        peer_ip = neighbor.get("peer-addr", "N/A")
        state = neighbor.get("state", "N/A")

        # Ensure VPN-ID is sortable as integer
        try:
            vpn_id_int = int(vpn_id)
        except ValueError:
            vpn_id_int = -1  # Invalid value fallback

        table_rows.append([hostname, vpn_id_int, asn, peer_ip, state])

# === Sort by Hostname then VPN-ID ===
table_rows.sort(key=lambda x: (x[0], x[1]))

# === Output ===
if table_rows:
    print("\n📊 BGP Neighbor Table:\n")
    print(tabulate(table_rows, headers=headers_row, tablefmt="fancy_grid"))

    # === Optional CSV Output ===
    if args.output:
        try:
            with open(args.output, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers_row)
                for row in table_rows:
                    writer.writerow(row)
            print(f"\n💾 CSV written to: {args.output}")
        except Exception as e:
            print(f"\n❌ Failed to write CSV: {e}")
else:
    print("\n⚠️ No BGP neighbor data found.")
