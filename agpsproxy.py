from fastapi import FastAPI, Request
from threading import Thread
from hypercorn.asyncio import serve
from hypercorn.config import Config
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import webdav3.client as webdav
import asyncio, time, os, json
import humanize

DIR_PREFIX = "agnss-data/"

# Web config
web_config = Config()
web_config.bind = ["0.0.0.0:443"]
web_config.certfile = "cert.pem"
web_config.keyfile = "key.pem"

# Load config
with open("config.json") as f:
    config = json.load(f)

app = FastAPI()

def download_orbits():
    while True:
        try:
            # Configure client with your credentials
            client = webdav.Client({
                'webdav_hostname': 'https://asp.gigacc.com/webdav',
                'webdav_login': config['username'] + ' ' + config['domain'],
                'webdav_password': config['password']
            })
            client.webdav.disable_check = True
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG950/cep_pak.bin")
            client.download_sync("top/1513^lle_data/GPS/lle_14days/lle_gps.lle", DIR_PREFIX + "BG951/lle_gps.lle")
            client.download_sync("top/1513^lle_data/GLONASS/lle_14days/lle_glo.lle", DIR_PREFIX + "BG951/lle_glo.lle")
            client.download_sync("top/1513^lle_data/Galileo/lle_14days/lle_gal.lle", DIR_PREFIX + "BG951/lle_gal.lle")
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG952/cep_pak.bin")
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG953/cep_pak.bin")
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG955/cep_pak.bin")
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG770/cep_pak.bin")
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG772/cep_pak.bin")
            client.download_sync("top/1513^cep_pak_1week/cep_pak.bin", DIR_PREFIX + "BG773/cep_pak.bin")
            [print(f"{path}: {humanize.naturalsize(os.path.getsize(path))}, {humanize.naturaldate(datetime.fromtimestamp(os.path.getmtime(path)))} {datetime.fromtimestamp(os.path.getmtime(path)).strftime('%H:%M:%S')}")
            for path in [DIR_PREFIX + f for f in ["BG950/cep_pak.bin", "BG951/lle_gps.lle", "BG951/lle_glo.lle", "BG951/lle_gal.lle"]]]
        except Exception as e:
            print(e)
        time.sleep(3590)  # Repeat every 1 hour

@app.middleware("http")
async def log_requests(request: Request, call_next):
    if request.url.path.startswith("/"):  # Log static file requests
        print(f"Static file request: {request.url.path}")
    response = await call_next(request)
    return response

if __name__ == "__main__":
    app.mount("/", StaticFiles(directory="agnss-data"), name="static")
    Thread(target=download_orbits, daemon=True).start()
    asyncio.run(serve(app, web_config))
