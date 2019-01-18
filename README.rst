NetFile Lobbyist API Sync Client
================================
Open source Python library to synchronize with the Lobbyist API data provided by NetFile, Inc.


Included in the project is a script named lobbyist_api_main.py. This script contains example usage of the lobbyist_api_client.py file by demonstrating the complete process of syncing lobbyist data. This includes.
    - Check system status to verify the Lobbyist API is available and in a ready state
    - Creates a Sync Subscription
    - Creates a Sync Session for the Sync Subscription. This will track whether or not your sync feed is up to date, or if there is more data available to sync
    - Syncs Lobbyist information which includes: Filings, Clients, Activity Expense, Campaign Contribution Made, ContactOfPublicOfficial, PaymentReceived, and Lobbyists
    - If the process runs successfully, the script Completes the Sync Session. This will let the API know that you have received the Sync Feed data successfully.
    - If any errors are encountered while running the process, the script will Cancel the Sync Session. This will tell the API that you have not received the data successfully. The next sync session for the subscription will start the sync from the last known Completed Sync Session
    - Finally, the Sync Subscription is cancelled. This step is mostly for demonstration purposes, as a Sync Subscription is usually maintained across many Sync Sessions, and does not need to be disposed of unless there will be no subsequent Sync Sessions required.

Usage
-----
1) Create config.json file based on the included config.json.example file
    - Create copy of config.json.example file named config.json
    - Update the API_KEY and API_PASSWORD values with API credentials provided from NetFile
2) Use the lobbyist_api_main.py file as a command line utility
    - `python lobbyist_api_,main.py --help`

System Requirements
-------------------
Python 3
    - Tested using python 3.7
Required libraries (These can be installed using Pip (example: $ pip install requests)
    - Requests Library


Log level output and Lobbyist API target environment are specified in lobbyist_api_client/src/__init__.py file

**Provided and supported by NetFile, Inc. The largest provider of Campaign and SEI services in California.**

More information:

- [Website] (https://www.netfile.com)
