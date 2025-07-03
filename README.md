# Overview
- Scripts developed for use with Cisco Catalyst SD-WAN vManage (formerly known as Viptela)
- Tested against 20.15 and 20.12

# Scripts

## Loss Latency Jitter
- Pulls the loss,latency & jitter parameters for SD-WAN tunnels out of vManage and populates a CSV file

## Cellular Quality
Pulls cellular radio information out of vManage for specified System-IP's and populates a CSV. Also makes a quality assessment for each radio parameter.

- RSSI: Received Signal Strength Indicator
- SNR: Signal-to-Noise Ratio

- RSRQ: Reference Signal Received Power
- RSRP: Reference Signal Received Quality


## Config Downloader
Pulls the running configuration of a managed device (i.e. sd-wan router) and saves it in a dated folder as a txt file

## BGP Status
Pulls the BGP status of each VRF/VPN's peer and sorts them in a table.
Use the **-o router-name.csv ** flag to output to CSV if reuqired.
