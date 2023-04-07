import requests, time, os, json, logging, configparser
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
from discord_webhook import DiscordWebhook, DiscordEmbed

# Define the path to the file to store the last release number
LAST_RELEASE_FILE = "last_release.txt"

# Track the start time of the script
start_time = time.time()

# Set up logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load secrets
secrets_file = 'secrets.ini'
if not os.path.isfile(secrets_file):
    # Create a new secrets file with a default webhook_url
    logging.warning(f'Secrets file {secrets_file} not found, creating new file with default values.')
    parser = configparser.ConfigParser()
    parser['DEFAULT'] = {'webhook_url': ''}
    with open(secrets_file, 'w') as f:
        parser.write(f)

parser = configparser.ConfigParser()
try:
    parser.read(secrets_file)
    webhook_url = parser['DEFAULT']['webhook_url']
except configparser.Error as e:
    logging.error(f'Error loading secrets file {secrets_file}: {e}')
    webhook_url = ''

if not webhook_url:
    logging.warning(f'No webhook_url found in secrets file {secrets_file}. Please add a webhook_url to receive updates.')

# Load config
config_file = 'config.ini'
if not os.path.isfile(config_file):
    # Create a new config file with a default check_frequency of 86400 seconds
    logging.warning(f'Config file {config_file} not found, creating new file with default values.')
    parser = configparser.ConfigParser()
    parser['DEFAULT'] = {'check_frequency': '86400'}
    with open(config_file, 'w') as f:
        parser.write(f)

parser = configparser.ConfigParser()
try:
    parser.read(config_file)
    check_frequency = int(parser['DEFAULT']['check_frequency'])
except configparser.Error as e:
    logging.error(f'Error loading config file {config_file}: {e}')
    check_frequency = 86400

logging.info(f'Successfully loaded secrets and config files.')

def postWebhook(loop_count, version_number):
    # Post update to Discord webhook
    if webhook is not None:
        webhook = DiscordWebhook(url=webhook_url)
        embed = DiscordEmbed(title='New Roblox Update!', color=242424)
        embed.add_embed_field(name='Client Update Checks', value=str(loop_count))
        embed.add_embed_field(name='New Version', value=version_number)
        embed.add_embed_field(name='Time Found', value=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        # Get the current uptime of the script
        uptime = time.time() - start_time

        # Convert uptime to a human-readable format
        uptime_str = str(timedelta(seconds=int(uptime)))

        # Add uptime to the Discord webhook embed field
        embed.add_embed_field(name='Uptime', value=uptime_str)
        webhook.add_embed(embed)
        response = webhook.execute()
        logging.info('Discord webhook response: %s', response)
    else:
        logging.info('Skipping webhook because webhook url is empty')

def getLatestReleaseNumber():
    url = 'https://create.roblox.com/docs/getting-started/overview'  # Roblox developer documentation
    try:
        # Send the GET request
        response = requests.get(url)

        # Check the response status code
        if response.status_code != 200:
            logger.error(f"Failed to get {url}. Response status code: {response.status_code}")
            return None

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the script tag with id '__NEXT_DATA__'
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

        if not script_tag:
            logger.error(f"No script tag found with id '__NEXT_DATA__' on {url}")
            return None

        # Get the contents of the script tag as a string
        json_string = script_tag.string

        # Parse the JSON string into a Python object
        j = json.loads(json_string)

        # Access the desired path in the JSON object
        release_path = j["props"]["pageProps"]["data"]["navigation"][7]["navigation"][2]["section"][0]["path"]

        # Split the release path by '/'
        path_parts = release_path.split('/')

        # Split end of path parts by '-'
        path_parts = path_parts[-1].split('-')
        # Get the last part of the path, which should be the release number
        release_number_str = path_parts[-1]

        try:
            # Convert the release number to an integer
            release_number = int(release_number_str)

        except ValueError as e:
            logger.error(f"Could not convert release number '{release_number_str}' to an integer: {e}")
            return None

        # Print the release number
        logger.info(f"Found new release number: {release_number}")

        return release_number

    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while making the request: {e}")
        return None

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"An error occurred while parsing the JSON: {e}")
        return None

# Initialize the last release number from the file or to None if the file does not exist
if os.path.isfile(LAST_RELEASE_FILE):
    with open(LAST_RELEASE_FILE, "r") as f:
        last_release_number = int(f.read().strip())
else:
    last_release_number = None

run_count = 0
while True:
    # Get the latest release number
    release_number = getLatestReleaseNumber()

    if release_number is not None:
        if release_number != last_release_number:
            if last_release_number is not None:
                # Log the run count and new release number
                logger.info(f"Run count: {run_count}, found new release number: {release_number}")
                postWebhook(run_count, release_number)
                # Write the new release number to the file
                with open(LAST_RELEASE_FILE, "w") as f:
                    f.write(str(release_number))
            else:
                # Log the initial release number
                logger.info(f"Initial release number: {release_number}")

                # Write the initial release number to the file
                with open(LAST_RELEASE_FILE, "w") as f:
                    f.write(str(release_number))

            # Update the last release number to the new release number
            last_release_number = release_number
        else:
            logging.info("Now new release found.")

    # Increment the run count
    run_count += 1

    logger.info(f"Waiting {check_frequency} seconds")
    # Wait before checking again
    time.sleep(check_frequency)