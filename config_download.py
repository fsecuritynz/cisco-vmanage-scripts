import requests
import urllib3
from getpass import getpass
from datetime import datetime
import re
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Hardcoded vManage connection details
vman_host_ip = "vmanage.com"
vman_port = "8443"
username = "yourusername"
password = "yourpassword"

# Prompt for one or more device IDs
device_ids_input = input("Enter deviceId(s), comma-separated: ")
device_ids = [d.strip() for d in device_ids_input.split(",") if d.strip()]

# Get current date/time info
now = datetime.now()
date_folder = now.strftime("%d-%m-%Y")
time_stamp = now.strftime("%d-%m-%Y_%H-%M")

# Create output folder if it doesn't exist
if not os.path.exists(date_folder):
    os.makedirs(date_folder)

# Setup session
session = requests.session()
login_url = f"https://{vman_host_ip}:{vman_port}/j_security_check"
token_url = f"https://{vman_host_ip}:{vman_port}/dataservice/client/token"

# Login
payload = {'j_username': username, 'j_password': password}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

response = session.post(url=login_url, data=payload, headers=headers, verify=False)
if response.status_code != 200 or 'html' in response.text.lower():
    print("❌ Login failed.")
    exit()

# Get token
token_response = session.get(url=token_url, verify=False)
if token_response.status_code == 200:
    token = token_response.text
    session.headers['X-XSRF-TOKEN'] = token
else:
    print("❌ Token fetch failed.")
    exit()

# Loop over all device IDs
for device_id in device_ids:
    print(f"\n🔍 Fetching config for deviceId: {device_id}")
    device_url = f"https://{vman_host_ip}:{vman_port}/dataservice/device/config?deviceId={device_id}"
    config_response = session.get(url=device_url, verify=False)

    if config_response.status_code != 200:
        print(f"❌ Failed to fetch config for {device_id}")
        continue

    config_text = config_response.text

    # Extract description
    match = re.search(r"^\s*description\s+(\S+)", config_text, re.MULTILINE)
    if match:
        prefix = match.group(1)
    else:
        prefix = f"device-{device_id}"

    filename = f"{prefix}_{time_stamp}.txt"
    filepath = os.path.join(date_folder, filename)

    with open(filepath, "w") as f:
        f.write(config_text)

    print(f"✅ Saved config to {filepath}")
