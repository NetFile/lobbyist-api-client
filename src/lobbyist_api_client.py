#!/usr/bin/python

import sys
from enum import Enum
import requests
from src import *

logger = logging.getLogger(__name__)


class Routes:
    SYSTEM_REPORT = '/system'
    SYNC_FEED = '/sync/feeds'
    SYNC_SUBSCRIPTIONS = '/sync/subscriptions'
    SYNC_SESSIONS = '/sync/sessions'

    # First parameter is Session ID. Second parameter is Command Type
    SYNC_SESSION_COMMAND = '/sync/sessions/%s/commands/%s'

    # First parameter is Subscription ID. Second parameter is Command Type
    SYNC_SUBSCRIPTION_COMMAND = '/sync/subscriptions/%s/commands/%s'

    # Parameter is the Subscription ID
    FETCH_SUBSCRIPTION = '/sync/subscriptions/%s'


class LobbyistApiClient:
    """Provides support for synchronizing local database with Lobbyist API filing data"""
    def __init__(self, base_url, api_key, api_password):
        self.headers = {
            'Content-type': 'application/json',
            'Accept': 'application/json'
        }
        self.base_url = base_url
        self.user = api_key
        self.password = api_password

    def fetch_system_report(self):
        logger.debug('Checking to verify the Lobbyist API system is ready')
        url = self.base_url + Routes.SYSTEM_REPORT
        sr = self.get_http_request(url)
        logger.debug('General Status: %s', sr['generalStatus'])
        logger.debug('System Name: %s', sr['name'])
        for comp in sr['components']:
            logger.debug('\tComponent Name: %s', comp['name'])
            logger.debug('\tComponent Message: %s', comp['message'])
            logger.debug('\tComponent status: %s', comp['status'])
            logger.debug('\tComponent Build DateTime: %s', comp['buildDateTime'])
            logger.debug('\tComponent Build Version: %s', comp['buildVersion'])
        return sr

    def create_subscription(self, subscription_name_arg):
        logger.debug('Creating a SyncSubscription')
        url = self.base_url + Routes.SYNC_SUBSCRIPTIONS
        body = {
            'name': subscription_name_arg,
            'autoComplete': False
        }
        return self.post_http_request(url, body)

    def create_session(self, sub_id, is_auto_complete=False):
        logger.debug(f'Creating a SyncSession using SyncSubscription {sub_id}')
        url = self.base_url + Routes.SYNC_SESSIONS
        body = {
            'subscriptionId': sub_id,
            'autoComplete': is_auto_complete
        }
        return self.post_http_request(url, body)

    # def retrieve_sync_feeds(self):
    #     logger.debug('Retrieving SyncFeed')
    #     url = self.base_url + Routes.SYNC_FEED
    #     return self.get_http_request(url)

    def fetch_sync_topics(self, session_id, topic, limit=1000, offset=0):
        logger.debug(f'Fetching {topic} topic: offset={offset}, limit={limit}\n')
        params = {'limit': limit, 'offset': offset}
        url = f'{self.base_url}/{Routes.SYNC_SESSIONS}/{session_id}/topics/{topic}'
        return self.get_http_request(url, params)

    def execute_session_command(self, session_id, session_command_type):
        logger.debug(f'Executing {session_command_type} SyncSession command')
        url = self.base_url + Routes.SYNC_SESSION_COMMAND % (session_id, session_command_type)
        return self.post_http_request(url)

    def execute_subscription_command(self, sub_id, subscription_command_type):
        logger.debug(f"Executing {subscription_command_type} SyncSubscription command")
        ext = Routes.SYNC_SUBSCRIPTION_COMMAND % (sub_id, subscription_command_type)
        url = self.base_url + ext
        body = {
            'id': sub_id
        }
        return self.post_http_request(url, body)

    def get_http_request(self, url, params=None, headers=None):
        logger.debug(f'Making GET HTTP request to {url}')
        if headers is None:
            headers = self.headers
        try:
            response = requests.get(url, params=params, auth=(self.user, self.password), headers=headers)
        except Exception as ex:
            logger.info(ex)
            sys.exit()
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        return response.json()

    def post_http_request(self, url, body=None):
        logger.debug(f'Making POST HTTP request to {url}')
        try:
            response = requests.post(url, auth=(self.user, self.password), data=json.dumps(body), headers=self.headers)
        except Exception as ex:
            logger.info(ex)
            sys.exit()
        if response.status_code not in [200, 201]:
            raise Exception(
                f'Error requesting Url: {url}, Response code: {response.status_code}. Error Message: {response.text}')
        return response.json()


class SyncSubscriptionCommandType(Enum):
    Unknown = 1
    Create = 2
    Edit = 3
    Cancel = 4


class SyncSessionCommandType(Enum):
    Unknown = 1
    Create = 2
    RecordRead = 3
    Complete = 4
    Cancel = 5
