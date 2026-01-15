# Wardriving-Wireless-Security-Analysis

## 📌 Project Overview

This project analyzes Wi-Fi networks collected via wardriving using Kismet, with a strong focus on ethical data handling and anonymization.
The goal is to demonstrate practical skills in wireless security assessment, data anonymization, Python scripting, and visualization, suitable for IT Security / SOC Analyst roles.

All collected data is anonymized before analysis and no raw or identifying data is published.

### 📽️ Demo
![WiFi map Demo](images/gifs/recording.gif)

### Live Map
👉 https://xxxxxx/

### 🗺️ Map Legend & Interpretation

- Each point represents an aggregated detection area, not an exact location
- Colors indicate dominant security type in the area:
  - Red: Open
  - Yellow: WEP
  - Blue: WPA2
  - Green: WPA3
- Locations are intentionally imprecise to protect privacy

## 🎯 Objectives

- Collect Wi-Fi metadata using Kismet during wardriving
- Anonymize all sensitive identifiers (SSID, BSSID, manufacturer, signal strength)
- Visualize anonymized data on an interactive map
- Summarize Wi-Fi security posture in the scanned area
- Follow ethical, legal, and responsible disclosure principles

## 🚧 Limitations & Non-Goals

- This project does NOT attempt to:
  - Identify individual networks or owners
  - Track devices over time
  - Perform intrusion or exploitation
- GPS accuracy is intentionally reduced
- Results reflect a limited geographic and temporal sample
- Security posture observations should not be generalized beyond the scanned area

## 🎓 Why This Project

This project was built to demonstrate:
- Understanding of wireless security fundamentals
- Ethical handling of sensitive data
- Python-based data processing
- Visualization of security-relevant information
- Awareness of privacy, legal, and ethical boundaries

It is intended as a learning and portfolio project, not a commercial tool.


## 🧰 Tools & Technologies

- Kismet – Wi-Fi packet capture and wardriving
- Python 3
 -SQLite (Kismet .kismet database format)
- Folium / Leaflet.js – interactive mapping
- Hashing (SHA-256 + salt) for anonymization

## 🔐 Data Anonymization & Ethics

This project does not publish raw wardriving data.

The following steps are applied before any analysis:

- SSIDs are hashed using SHA-256 with a random user-defined salt
- BSSIDs (MAC addresses) are hashed
- GPS coordinates are rounded (to the third decimal)
- Signal strength is removed
- Manufacturers are replaced with fictional company names
- Timestamps are removed

⚠️ Raw Kismet capture files are intentionally excluded from this repository.

## 📊 Scan Results and Analysis

![My scan results summarized.](images/results.png)

Key Observations

- The majority of networks use WPA2, indicating reasonable but aging security
- WPA3 adoption is still low
- A notable percentage of open networks, including IoT devices
- Legacy protocols (WEP) are rare but still present

## 🛠️ Environment Setup & Map Generation (Windows 11)

This guide explains how the Python environment was set up on Windows 11 to process Kismet data and generate the interactive map.
Although I scanned the networks using Parrot OS (Linux), I later transfered the .kismet scan results to my windows machine where I did all the scripting and map generation etc. I will give a short summary below of how I setp up my windows to enable python scripting and map generation:

1. Navigate to the official Python website: https://www.python.org/downloads/windows/.
   - Download the latest Python version and run the installer.
   - In the installer, check 'Add Python to path'.
   -  Open Powershell and confirm the Python installation:

```
python --version
pip --version
```
2. Install the required python libraries for this project:

```
pip install pandas folium
```
 - Verify:
```
python -c "import pandas, folium; print('Libraries installed successfully')"
```

3. Create the 1st python anonymization script:

> [!NOTE]
> If you are going to create a map straight from the raw data with no anonymization, skip to step 5.

  - Create a new file and name it appropriately e.g.: anonymize_kismet_data.py
  -  Pull or add the data anonymization script under /scripts in this repo.
  
> [!IMPORTANT]
> Make sure the file extension is .py if creating the file manually.

4. Run the script
  - From Powershell in the folder (hold shift and right-click in the folder with the python script -> then run Powershell
```
python scripts\kismet_to_map.py
```

5. Create the 2nd python folium map generation script:
  - Create a new file and name it appropriately e.g.: anonymize_kismet_data.py
  - Pull or add the map generation script under /scripts in this repo.

6. Run the script
  - From Powershell in the folder (hold shift and right-click in the folder with the python script -> then run Powershell
```
python scripts\generate_folium_map_anonymized.py
```
  - This will output a file named: wifi_security_map.html in the same folder. Opening this with your browser shows you the folium map!




