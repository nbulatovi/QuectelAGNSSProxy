# Quectel AGNSS proxy for SONY modules

This document covers:
1) How to mirror long-term orbits from SONY AGNSS server and host the orbit files on a proxy web server.
2) How to configure Quectel GNSS-enabled modules for proxy server access to XTRA orbits.

## Key Features

- **Automated Data Downloads**: Downloads updated orbital data files from SONY WebDAV server every hour to keep data current.
- **Longest Available Orbits**: For each Quectel module, proxy app will select the orbit file with longest validity (7-14 days).
- **Supported Quectel Modules**: All Quectel LPWA modules with SONY chipset and GNSS.
- **Web Server**: A FastAPI server serves static files, allowing users to access downloaded data through a web interface.
- **Secure Access**: The server runs on HTTPS, ensuring encrypted communication when accessing the data files.
- **Data Monitoring**: The program logs the size and modification time of the downloaded orbit files for monitoring purposes.

## Components

1. **FastAPI Web Server**:
    - Proxy app uses FastAPI to serve static files from the `agnss-data/` directory.
    - It listens on port 443 for secure (HTTPS) connections.
    - SSL certificates (`cert.pem` and `key.pem`) are used for secure communication.

2. **WebDAV Client**:
    - Description of WebDAV interface can be found in BG77xA-GL&BG95xA-GL GNSS Application Note.
    - The `webdav3` Python library is used to interact with the WebDAV server.
    - Credentials (username, domain, and password) are stored in the `config.json` file and used to authenticate the WebDAV client.

3. **Background Task (Download Orbits)**:
    - A background thread downloads orbital data every hour from the WebDAV server.
    - The following data is downloaded:
      - `cep_pak.bin`: Orbital data for BG950 and BG952 modules.
      - `lle_gps.lle`, `lle_glo.lle`, `lle_gal.lle`: Orbit data for GPS, GLONASS, and Galileo for BG951.
    - The sizes and modification times of the downloaded files are logged for monitoring.

4. **Data Storage and Access**:
    - Downloaded data is stored in directories (e.g., `BG950`, `BG951`, `BG952`) under the `agnss-data/` directory.
    - The data can be accessed via the web server at URLs like `https://yourserveraddress/BG950/cep_pak.bin`.

## How It Works

1. **Startup**: Upon application startup, it loads configuration settings from the `config.json` file (which includes WebDAV credentials).
2. **Data Download**: The `download_orbits` function runs every hour, downloading updated orbital data files from the WebDAV server. It fetches the following:
    - `cep_pak.bin` (orbital data for multiple satellite systems).
    - `lle_gps.lle`, `lle_glo.lle`, `lle_gal.lle` (LLE data for GPS, GLONASS, and Galileo satellites).
3. **Serving Files**: The FastAPI web server makes the downloaded data files available via HTTP. Users can access the data files from the server at URLs like `https://yourserveraddress/BG950/cep_pak.bin`.


## Requirements

Python 3.13+

Install dependencies with:

```bash
pip install fastapi hypercorn webdavclient3 humanize
```

## Example config.json configuration file

```
{
    "username": "sony_username",
    "domain": "gps-cep",
    "password": "sony_password"
}
```

## Demo Server Hosted on AWS

Quectel is hosting a demo server for its customers. You can access the server at the following IP address:

```
44.228.248.147
```

## Example Modem AT commands

Commands to enable XTRA feature and configure proxy server on BG950 module:

```
AT+QGPSXTRA=1
AT+CFUN=1,1
AT+QGPSCFG="xtra_cfg","https://44.228.248.147/BG950/cep_pak.bin"
AT+QGPSCFG="xtrafilesize",7
```

## Qecduino example

Quecduino is an Arduino ESP32 library example showing how to command Quectel LPWA modules to:
* Configure connection to Quectel AGNSS demo proxy server
* Download XTRA AGNSS aiding file

It is located at: https://github.com/nbulatovi/Quecduino
