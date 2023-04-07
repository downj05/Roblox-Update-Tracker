# ROBLOX Update Checker

This is a Python script that periodically checks Roblox for the latest release number and notifies the user via a Discord webhook if it has changed.

## Installation

1. Clone this repository to your local machine.
2. Install the required modules using the following command: `pip install -r requirements.txt`
3. Copy the `secrets.example.ini` and `config.example.ini` files to `secrets.ini` and `config.ini`, respectively.
4. Update the `secrets.ini` file with your Discord webhook URL and the `config.ini` file with your desired check frequency.

## Usage

To run the script, use the following command:
```python main.py```

The script will start checking for the latest release number and will notify the user via Discord webhook if the number has changed.

![Execution example](https://cdn.discordapp.com/attachments/588629635420520454/1093834775405543424/image.png)
![Webhook example](https://cdn.discordapp.com/attachments/588629635420520454/1093834723509424218/image.png)
