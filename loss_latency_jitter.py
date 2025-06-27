import requests
import urllib3
import json
import csv
from getpass import getpass

def authentication(user, password, vman_host_ip, vman_port):
    if not vman_host_ip:
        exit("ERROR <<<:::>>> vManage hostname or URL not provided")
    if not user:
        exit("ERROR <<<:::>>> Username not provided")
    if not password:
        exit("ERROR <<<:::>>> Password not provided")
    
    urllib3.disable_warnings()
    url = f"https://{vman_host_ip}:{vman_port}/j_security_check"
    payload = f'j_username={user}&j_password={password}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("ERROR <<<:::>>> ", e)
        exit()

    cookie = response.headers['set-cookie']
    url = f"https://{vman_host_ip}:{vman_port}/dataservice/client/token"
    headers = {
        'Content-Type': 'application/json',
        'Cookie': cookie,
    }
    response = requests.request("GET", url, headers=headers, data={}, verify=False)
    xsrf = response.text
    if "<html>" in xsrf:
        exit("ERROR <<<:::>>> Invalid or Locked Credentials")
    return cookie, xsrf

# Replace with your actual values
def userinputs():
    vman_host_ip = "vmanage.cisco.com" # Update to your vManage hostname
    vman_port = "8443" # Do NOT change this to 443
    user = "your-username" # Update to your Username
    password = "your-password" # Update to your Password
    return user, password, vman_host_ip, vman_port

user, password, vman_host_ip, vman_port = userinputs()
c, x = authentication(user, password, vman_host_ip, vman_port)

hrs = "1"

url = f"https://{vman_host_ip}:{vman_port}/dataservice/statistics/approute/tunnels/health/latency?limit=10000&last_n_hours={hrs}"
headers = {
    'Content-Type': 'application/json',
    'X-XSRF-TOKEN': x,
    'Cookie': c,
}

response = requests.request("GET", url, headers=headers, data={}, verify=False)
tunneldetails = json.loads(response.text)['data']
epoch = json.loads(response.text)['header']['generatedOn']

getdevurl = f"https://{vman_host_ip}:{vman_port}/dataservice/health/devices?page_size=12000"
devlist = json.loads((requests.request("GET", getdevurl, headers=headers, data={}, verify=False)).text)['devices']

for i in range(0, len(tunneldetails)):
    for j in range(0, len(devlist)):
        if tunneldetails[i]['local_system_ip'] == devlist[j]['system_ip']:
            tunneldetails[i]['local_system_ip'] = devlist[j]['name']
        if tunneldetails[i]['remote_system_ip'] == devlist[j]['system_ip']:
            tunneldetails[i]['remote_system_ip'] = devlist[j]['name']

def get_rating(value, poor_threshold, average_threshold):
    if value > poor_threshold:
        return 'Poor'
    elif value > average_threshold:
        return 'Average'
    else:
        return 'Good'

for tunnel in tunneldetails:
    tunnel['Loss Rating'] = get_rating(tunnel['loss_percentage'], 1, 0.1)
    tunnel['Latency Rating'] = get_rating(tunnel['latency'], 150, 50)
    tunnel['Jitter Rating'] = get_rating(tunnel['jitter'], 30, 10)

with open('file_'+str(epoch)+'.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['Local Endpoint', 'Local Color', 'Remote Endpoint', 'Remote Color', 'Loss', 'Loss Rating', 'Latency', 'Latency Rating', 'Jitter', 'Jitter Rating', 'State'])
    writer.writeheader()
    for tunnel in tunneldetails:
        writer.writerow({
            'Local Endpoint': tunnel['local_system_ip'],
            'Local Color': tunnel['local_color'],
            'Remote Endpoint': tunnel['remote_system_ip'],
            'Remote Color': tunnel['remote_color'],
            'Loss': tunnel['loss_percentage'],
            'Loss Rating': tunnel['Loss Rating'],
            'Latency': tunnel['latency'],
            'Latency Rating': tunnel['Latency Rating'],
            'Jitter': tunnel['jitter'],
            'Jitter Rating': tunnel['Jitter Rating'],
            'State': tunnel['state']
        })

print("Stats exported to :>>> " + ('file_'+str(epoch)+'.csv'))
