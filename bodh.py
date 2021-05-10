import click
import requests
import json
from os import path, makedirs
from time import sleep
from config_path import ConfigPath

default_host = "https://bodh.iotready.co"

conf_path = ConfigPath( 'bodh', 'iotready.co', '.json' )
file_path = conf_path.saveFilePath( mkdir=False )


@click.group()
def cli():
    pass


@cli.command()
@click.option('--host', default=default_host, prompt="Bodh host", help='Bodh host (for self-hosted).')
@click.option('--apikey', prompt='Admin API key', help='Admin API key to save.')
def configure(host, apikey):
    """Save host and apikey in the user's config directory."""
    config = {
        "api_key": apikey,
        "host": host,
    }
    with open(file_path, "w") as f:
        json.dump(config, f)
    click.echo('Stored config at: %s' % file_path)


def read_saved_config():
    path = conf_path.readFilePath()
    assert path, "Could not locate config file. Please run `bodh configure` first."

    with open(file_path, "r") as f:
        config = json.load(f)
    host = config['host']
    api_key = config['api_key']
    
    assert host and api_key, "Could not detect host or API key. Please run `bodh configure` again."
    return host, api_key

@cli.command()
@click.option('--deviceid', prompt='Device ID', help='ID of device to register')
def register(deviceid):
    """Register a device using the apikey."""

    host, api_key = read_saved_config()

    url = host + "/api/devices"
    payload = {
        "device": {
            "id": deviceid
        }
    }
    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }

    res = requests.post(url, data = json.dumps(payload), headers = headers)
    
    data = res.json()
    base_path = "certs/{}".format(deviceid)
    mkdir(base_path)
    for key, url in data.items():
        download_file(url, base_path)
    click.echo("Use the saved certifcates to connect device with ID {} to AWS IoT!".format(deviceid))

def download_file(url, base_path):
    r = requests.get(url, allow_redirects=True)
    file_name = get_file_name(url)
    file_path = path.join(base_path, file_name)
    print("Downloading", file_path)
    with open(file_path, 'wb') as f:
        f.write(r.content)
        

def get_file_name(url):
    return url.split('?')[0].split('/')[-1]

def mkdir(path):
    makedirs(path, exist_ok=True)

@cli.command()
@click.option('--deviceid', prompt='Device ID', help='ID of device for which to send a test event.')
@click.option('--interval', prompt='Interval', default=10, type=int, help='Interval between test events (min = 5s).')
def simulate(deviceid, interval):
    """Sends `MAX` test events using the apikey."""
    MAX = 10

    if interval < 5:
        interval = 5
        print("Using min interval of 5s")

    host, api_key = read_saved_config()

    url = host + "/api/events"
    payload = {
        "event": {
            "device_id": deviceid,
            "data": {
                "metric1": 100,
                "metric2": 0.005,
                "metric3": "dry"
            }
        }
    }
    headers = {
        'Accept': 'application/json',
        'x-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    for i in range(0, MAX):
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        data = res.json()
        click.echo(data)
        sleep(interval)

if __name__ == '__main__':
    cli()
