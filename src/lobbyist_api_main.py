#!/usr/bin/python

import sys
from lobbyist_api_client import LobbyistApiClient, SyncSubscriptionCommandType, SyncSessionCommandType
from src import *


def main():
    """
    This demonstrates the complete lifecycle of the Lobbyist API sync process.
    1) Create a SyncSubscription
    2) Create a SyncSession using the SyncSubscription. This will be the start of the session
    3) Synchronize Filing Activities
    4) Synchronize Element Activities
    5) Synchronize Transaction Activities
    5) Complete the SyncSession. This will be the end of the session
    6) Cancel the SyncSubscription. SyncSubscriptions are long living, and do not need to be canceled between SyncSessions
    """
    sync_session = None
    api_client = None
    try:
        logger.info('Starting Lobbyist API synchronization lifecycle')
        api_client = LobbyistApiClient(api_url, api_key, api_password)

        # Verify the system is ready
        sys_report = api_client.fetch_system_report()
        if sys_report['generalStatus'].lower() == 'ready':
            logger.info('Lobbyist API Sync is Ready')

            # Retrieve available SyncFeeds
            logger.info('Retrieving available Lobbyist sync feed')
            feeds = api_client.retrieve_sync_feeds()
            feed = feeds[0]

            # Create SyncSubscription or use existing SyncSubscription with feed specified
            name = 'My Lobbyist API Feed'
            logger.info('Creating new subscription with name "%s"', name)
            subscription_response = api_client.create_subscription(feed.name, name)

            # Create SyncSession
            logger.info('Creating sync session')
            subscription = subscription_response.subscription
            sync_session_response = api_client.create_session(subscription.id)

            if sync_session_response.sync_data_available:
                logger.info('Synchronizing Filing Activities')
                sync_session = sync_session_response.session

                offset = 0
                page_size = 25
                logger.info('Synchronizing Filing Activities')
                filings_qr = api_client.fetch_sync_topics(sync_session.id, 'filing-activities', page_size, offset)
                while filings_qr.hasNextPage:
                    offset = offset + page_size
                    filings_qr = api_client.fetch_sync_topics(sync_session.id, 'filing-activities', page_size, offset)

                offset = 0
                logger.info('Synchronizing Element Activities')
                elements_qr = api_client.fetch_sync_topics(sync_session.id, 'element-activities', page_size, offset)
                while elements_qr.hasNextPage:
                    offset = offset + page_size
                    elements_qr = api_client.fetch_sync_topics(sync_session.id, 'element-activities', page_size, offset)

                # Complete SyncSession
                logger.info('Completing sync session')
                api_client.execute_session_command(sync_session.id, SyncSessionCommandType.Complete.name)

                # Cancel the subscription
                logger.info('Canceling subscription')
                api_client.execute_subscription_command(subscription.id, SyncSubscriptionCommandType.Cancel.name)

                logger.info('Synchronization lifecycle complete')
            else:
                logger.info('No Sync Data Available. Nothing to retrieve')
        else:
            logger.info('The Lobbyist API system status is %s and is not Ready', sys_report.general_status)
    except Exception as ex:
        # Cancel Session on error
        if sync_session is not None:
            logger.info('Error occurred, canceling sync session')
            api_client.execute_session_command(sync_session.id, SyncSessionCommandType.Cancel.name)
        logger.error('Error running LobbyistApiClient: %s', ex)
        sys.exit()


if __name__ == '__main__':
    main()
