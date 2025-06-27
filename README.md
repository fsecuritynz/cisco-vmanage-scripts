# Loss Latency Jitter
- Pulls the loss,latency & jitter parameters for SD-WAN tunnels out of vManage and populates a CSV file

# Cellular Quality
- Pulls cellular radio information out of vManage for specified System-IP's and populates a CSV. Also makes a quality assessment for each radio parameter.
- RSSI: Received Signal Strength Indicator

If radio-rssi >= -69 then radio-rssi-rating = Excellent

If radio-rssi >= -89 then radio-rssi-rating = Good

If radio-rssi >= -99 then radio-rssi-rating = Fair

else radio-rssi-rating = Poor


- SNR: Signal-to-Noise Ratio

If radio-snr >= 20 then radio-snr-rating = Excellent

If radio-snr >= 13 then radio-snr-rating  = Good

If radio-snr >= 5 then radio-snr-rating = Fair

else radio-snr = Poor


- RSRQ: Reference Signal Received Power

If radio-rsrq >= -10 then  radio-rsrq-rating = Excellent

If radio-rsrq >= -15 then  radio-rsrq-rating = Good

If radio-rsrq >= -19 then  radio-rsrq-rating = Fair

else  radio-rsrq-rating = Poor


- RSRP: Reference Signal Received Quality
If radio-rsrp >= -80 then radio-rsrp-rating = Excellent

If radio-rsrp >= -90 then radio-rsrp-rating = Good

If radio-rsrp >= -99 then radio-rsrp-rating = Fair

else radio-rsrp-rating = Poor
