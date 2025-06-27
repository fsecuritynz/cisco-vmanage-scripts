import requests
import urllib3
import json
import csv
from datetime import datetime
from getpass import getpass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace with your actual values
vman_host_ip = "vmanage.cisco.com" # Update to your vManage hostname
vman_port = "8443" # Do not change this to 443
username = "your-username" # Update to your Username
password = "your-password" # Update to your password

# Define the various System IPs
device_ips = ["1.1.30.2"] # Multiple entires are possible i.e. ["1.1.30.2", "1.1.30.3"]

# Login URL and session setup
session = requests.session()
login_url = f"https://{vman_host_ip}:{vman_port}/j_security_check"
token_url = f"https://{vman_host_ip}:{vman_port}/dataservice/client/token"

# Login payload
payload = {'j_username': username, 'j_password': password}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

# Login to vManage
response = session.post(url=login_url, data=payload, headers=headers, verify=False)

if response.status_code != 200 or 'html' in response.text.lower():
    print("Login failed.")
    exit()

# Get token
token_response = session.get(url=token_url, verify=False)
if token_response.status_code == 200:
    token = token_response.text
    session.headers['X-XSRF-TOKEN'] = token
else:
    print("Token fetch failed.")
    exit()



# Output filename with timestamp
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
csv_filename = f"radio-{timestamp}.csv"

# CSV Fields
fields = [
    "vdevice-host-name",
    "cellular-interface",
    "vdevice-name",
    "radio-rat-selected",
    "radio-band",
    "bandwidth",
    "radio-tx-channel",
    "radio-rx-channel",
    "radio-rssi",
    "radio-rssi-rating",
    "radio-snr",
    "radio-snr-rating",
    "radio-rsrq",
    "radio-rsrq-rating",
    "radio-rsrp",
    "radio-rsrp-rating",
    "nr5g-rxch",
    "nr5g-txch",
    "nr5g-band",
    "nr5g-rssi",
    "nr5g-snr",
    "nr5g-rsrq",
    "nr5g-rsrp",
    "lastupdated"  # 
]

# Open CSV and write all device data
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()

    for device_id in device_ips:
        print(f"Fetching data for deviceId: {device_id}")
        radio_url = f"https://{vman_host_ip}:{vman_port}/dataservice/device/cellular/radio?deviceId={device_id}"
        radio_response = session.get(url=radio_url, verify=False)

        if radio_response.status_code != 200:
            print(f"Failed to fetch radio data for {device_id}")
            continue

        radio_data = radio_response.json().get("data", [])

        for entry in radio_data:
            # Skip if it's not the target interface - in this case Cellular0/2/0
            if entry.get("cellular-interface") != "Cellular0/2/0":
                continue

            row = {key: entry.get(key, "") for key in fields}

            # Signal value conversions
            try:
                rssi = int(entry.get("radio-rssi", -999))
                snr = float(entry.get("radio-snr", -999))
                rsrq = int(entry.get("radio-rsrq", -999))
                rsrp = int(entry.get("radio-rsrp", -999))
            except ValueError:
                rssi = snr = rsrq = rsrp = -999

            # radio-rssi rating
            if rssi >= -69:
                row["radio-rssi-rating"] = "Excellent"
            elif rssi >= -89:
                row["radio-rssi-rating"] = "Good"
            elif rssi >= -99:
                row["radio-rssi-rating"] = "Fair"
            else:
                row["radio-rssi-rating"] = "Poor"

            # radio-snr rating
            if snr >= 20:
                row["radio-snr-rating"] = "Excellent"
            elif snr >= 13:
                row["radio-snr-rating"] = "Good"
            elif snr >= 5:
                row["radio-snr-rating"] = "Fair"
            else:
                row["radio-snr-rating"] = "Poor"

            # radio-rsrq rating
            if rsrq >= -10:
                row["radio-rsrq-rating"] = "Excellent"
            elif rsrq >= -15:
                row["radio-rsrq-rating"] = "Good"
            elif rsrq >= -19:
                row["radio-rsrq-rating"] = "Fair"
            else:
                row["radio-rsrq-rating"] = "Poor"

            # radio-rsrp rating
            if rsrp >= -80:
                row["radio-rsrp-rating"] = "Excellent"
            elif rsrp >= -90:
                row["radio-rsrp-rating"] = "Good"
            elif rsrp >= -99:
                row["radio-rsrp-rating"] = "Fair"
            else:
                row["radio-rsrp-rating"] = "Poor"

            # Format 'lastupdated' timestamp
            if "lastupdated" in entry and isinstance(entry["lastupdated"], int):
                row["lastupdated"] = datetime.fromtimestamp(
                    entry["lastupdated"] / 1000
                ).strftime("%d %b %Y %I:%M:%S %p")

            writer.writerow(row)

print(f"\n✅ Radio data written to {csv_filename}")
