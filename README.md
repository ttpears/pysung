# Samsung TV Remote Control

This script allows you to control a Samsung TV remotely using Python. It uses the Samsung Smart TV WebSocket API library to communicate with the TV and perform various operations such as turning the TV on/off, opening apps, and more.

## Installation

To use this script, you need to install the following dependencies:

- **samsungtvws**: This library provides a WebSocket client implementation for the Samsung Smart TV WebSocket API. Install it using pip:

# Samsung TV Remote Control

This script allows you to control a Samsung TV remotely using Python. It uses the Samsung Smart TV WebSocket API library to communicate with the TV and perform various operations such as turning the TV on/off, opening apps, and more.

## Installation

To use this script, you need to install the following dependencies:

```
pip install wakeonlan samsungtvws termcolor
```


## Usage

To use this script, follow the steps below:

1. Connect your computer and Samsung TV to the same network.

2. Find out the IP or hostname of your Samsung TV.

3. Run the script with the following command:

`python tv.py tvHost [command] [args]`

- `tvHost`: IP or hostname of the Samsung TV.

- `command` (optional): Command to execute.

- `args` (optional): Arguments for the command.

Available commands:

- `toggle_power`: Toggle power of the TV.

- `power_on`: Power on the TV using Wake-on-LAN (WoL) magic packets.

- `open_web <url>`: Open a web page in the TV's browser.

- `view_installed_apps`: View the list of installed apps on the TV.

- `open_app <appName>`: Open a specific app on the TV.

- `get_app_status <appName>`: Get the status of a specific app on the TV.

- `run_app <appName>`: Run a specific app on the TV.

- `close_app <appName>`: Close a specific app on the TV.

- `install_app <appName>`: Install a specific app from the official store on the TV.

- `get_device_info`: Get information about the TV.

## License

This script is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
