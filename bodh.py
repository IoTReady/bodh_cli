import click
import http.client
import json
import os
from config_path import ConfigPath

default_host = "localhost"
default_port = 4000

conf_path = ConfigPath( 'bodh', 'iotready.co', '.json' )
file_path = conf_path.saveFilePath( mkdir=False )

path = conf_path.readFilePath()
if path is not None:
    with open(file_path, "r") as f:
        config = json.load(f)
else:
    config = {}


@click.group()
def cli():
    pass


@cli.command()
@click.option('--host', default=default_host, prompt="Bodh host", help='Bodh host (for self-hosted).')
@click.option('--port', default=default_port, prompt="Bodh host port", help='Bodh host port (for self-hosted).')
@click.option('--secure', default=True, prompt="Use SSL", help='Use SSL to connect.')
@click.option('--apikey', prompt='Admin API key', help='Admin API key to save.')
def save(host, port, secure, apikey):
    """Save host and apikey in the user's config directory."""
    config = {
        "apikey": apikey,
        "host": host,
        "port": port,
        "secure": secure
    }
    with open(file_path, "w") as f:
        json.dump(config, f)
    click.echo('Stored config at: %s' % file_path)


@cli.command()
@click.option('--host', default=config.get('host') or default_host, help='Bodh host (for self-hosted).')
@click.option('--port', default=config.get('port') or default_port, help='Bodh host (for self-hosted).')
@click.option('--secure', default=config.get('secure'), help='Bodh host (for self-hosted).')
@click.option('--apikey', default=config.get('apikey'), prompt='Admin API key', help='Admin API key.')
@click.option('--deviceid', prompt='Device ID',
              help='ID of device to register')
def register(host, port, secure, apikey, deviceid):
    """Register a device using the apikey."""
    api_endpoint = "/api/devices"
    if secure:
        conn = http.client.HTTPSConnection(host, port)
    else:
        conn = http.client.HTTPConnection(host, port)
    payload = json.dumps({
    "device": {
        "id": deviceid
    }
    })
    headers = {
    'Accept': 'application/json',
    'x-api-key': apikey,
    'Content-Type': 'application/json'
    }
    conn.request("POST", api_endpoint, payload, headers)
    res = conn.getresponse()
    data = res.read()
    click.echo(data.decode("utf-8"))


@cli.command()
@click.option('--host', default=config.get('host') or default_host, help='Bodh host (for self-hosted).')
@click.option('--port', default=config.get('port') or default_port, help='Bodh host (for self-hosted).')
@click.option('--secure', default=config.get('secure'), help='Bodh host (for self-hosted).')
@click.option('--apikey', default=config.get('apikey'), prompt='Admin API key', help='Admin API key.')
@click.option('--deviceid', prompt='Device ID',
              help='ID of device for which to send a test event.')
def sendevent(host, port, secure, apikey, deviceid):
    """Sends a test event using the apikey."""
    api_endpoint = "/api/events"
    if secure:
        conn = http.client.HTTPSConnection(host, port)
    else:
        conn = http.client.HTTPConnection(host, port)
    payload = json.dumps({
        "event": {
            "device_id": deviceid,
            "data": {
                "metric1": 100,
                "metric2": 0.005,
                "metric3": "dry"
            }
        }
    })
    headers = {
    'Accept': 'application/json',
    'x-api-key': apikey,
    'Content-Type': 'application/json'
    }
    conn.request("POST", api_endpoint, payload, headers)
    res = conn.getresponse()
    data = res.read()
    click.echo(data.decode("utf-8"))

if __name__ == '__main__':
    cli()
