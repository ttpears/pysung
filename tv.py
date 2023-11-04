import sys
import os
import logging
import wakeonlan
import json
import sqlite3
from termcolor import colored

sys.path.append('../')

from samsungtvws import SamsungTVWS

TOKENS_DB = 'tv-tokens.db'

def get_authentication_token(tvHost):
    conn = sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT token FROM tokens WHERE host = ?', (tvHost,))
    token = cursor.fetchone()
    conn.close()
    return token[0] if token else None

def save_authentication_token(tvHost, token):
    conn = sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO tokens (host, token) VALUES (?, ?)', (tvHost, token))
    conn.commit()
    conn.close()

def create_tables():
    conn = sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tokens (
        host TEXT PRIMARY KEY,
        token TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_mapping (
        app_id TEXT PRIMARY KEY,
        app_name TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        host TEXT PRIMARY KEY,
        mac TEXT
    )
    ''')
    conn.commit()
    conn.close()

def get_wake_on_lan_mac(tvHost):
    conn = sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT mac FROM devices WHERE host = ?', (tvHost,))
    mac_address = cursor.fetchone()
    conn.close()
    return mac_address[0] if mac_address else None

def save_wake_on_lan_mac(tvHost, mac_address):
    conn =sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO devices (host, mac) VALUES (?, ?)', (tvHost, mac_address))
    conn.commit()
    conn.close()

def get_device_info(tv):
    info = tv.rest_device_info()
    mac_address = info['device']['wifiMac']
    save_wake_on_lan_mac(tv.host, mac_address)
    json_str = json.dumps(info, indent=4)
    colored_json = colored(json_str, 'red')
    print(colored_json)
    return mac_address

def print_help():
    help_message = """Usage: python script.py tvHost [command] [args]

    tvHost            - IP or hostname of the TV
    command           - Command to execute (optional)
    args              - Arguments for the command (optional)

    Commands:
    toggle_power            - Toggle power
    power_on                - Power on
    open_web <url>          - Open web in browser
    view_installed_apps     - View installed apps
    open_app <appName>      - Open an app
    get_app_status <appName>  - Get app status
    run_app <appName>         - Run an app
    close_app <appName>       - Close an app
    install_app <appName>     - Install an app from official store
    get_device_info         - Get device information"""

    print(help_message)

def main(tvHost, command=None, args=[]):
    # Increase debug level
    logging.basicConfig(level=logging.INFO)

    # Check if token file exists
    token_file = os.path.join(os.getcwd(), 'tv-token-' + tvHost + '.txt')
    if not os.path.exists(token_file):
        # Create empty token file
        with open(token_file, 'w') as file:
            pass

    # Create TV object
    tv = SamsungTVWS(host=tvHost, port=8002, token_file=token_file)

    if not get_wake_on_lan_mac(tvHost):
        mac_address = get_device_info(tv)
        save_wake_on_lan_mac(tvHost, mac_address)

    if command == 'toggle_power':
        tv.shortcuts().power()
    elif command == 'power_on':
        mac_address = get_wake_on_lan_mac(tvHost)
        wakeonlan.send_magic_packet(mac_address)
    elif command == 'open_web':
        url = args[0] if len(args) > 0 else None
        tv.open_browser(url)
    elif command == 'view_installed_apps':
        apps = tv.app_list()
        for app in apps:
            app_id = app['appId']
            app_name = app['name']
            save_app_mapping(app_id, app_name)

        json_str = json.dumps(apps, indent=4)
        colored_json = colored(json_str, 'cyan')
        print(colored_json)
    elif command == 'open_app':
        app_name = args[0] if len(args) > 0 else None
        app_id = get_app_id(app_name)
        if app_id:
            tv.run_app(app_id)
        else:
            print(f"App '{app_name}' is not installed")
    elif command == 'get_app_status':
        app_name = args[0] if len(args) > 0 else None
        app_id = get_app_id(app_name)
        if app_id:
            app = tv.rest_app_status(app_id)
            logging.info(app)
        else:
            print(f"App '{app_name}' is not installed")
    elif command == 'run_app':
        app_name = args[0] if len(args) > 0 else None
        app_id = get_app_id(app_name)
        if app_id:
            app = tv.rest_app_run(app_id)
            logging.info(app)
        else:
            print(f"App '{app_name}' is not installed")
    elif command == 'close_app':
        app_name = args[0] if len(args) > 0 else None
        app_id = get_app_id(app_name)
        if app_id:
            app = tv.rest_app_close(app_id)
            logging.info(app)
        else:
            print(f"App '{app_name}' is not installed")
    elif command == 'install_app':
        app_name = args[0] if len(args) > 0 else None
        app_id = get_app_id(app_name)
        if app_id:
            app = tv.rest_app_install(app_id)
            logging.info(app)
        else:
            print(f"App '{app_name}' is not installed")
    elif command == 'get_device_info':
        get_device_info(tv)
    else:
        print_help()

def get_app_id(app_name):
    conn = sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT app_id FROM app_mapping WHERE app_name LIKE ?', ('%'+app_name+'%',))
    app_id = cursor.fetchone()
    conn.close()
    return app_id[0] if app_id else None

def save_app_mapping(app_id, app_name):
    conn = sqlite3.connect(TOKENS_DB)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO app_mapping (app_id, app_name) VALUES (?, ?)', (app_id, app_name))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    tvHost = sys.argv[1]
    command = None
    args = []

    if len(sys.argv) >= 3:
        command = sys.argv[2]

    if len(sys.argv) >= 4:
        args = sys.argv[3:]

    if not os.path.exists(TOKENS_DB):
        create_tables()

    main(tvHost, command, args)

