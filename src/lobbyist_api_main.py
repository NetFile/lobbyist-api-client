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

            # Create SyncSubscription or use existing SyncSubscription with feed specified
            name = 'My Lobbyist API Feed'
            logger.info('Creating new subscription with name "%s"', name)
            subscription_response = api_client.create_subscription(name)
            subscription = subscription_response['subscription']

            # Create SyncSession
            logger.info('Creating sync session')
            auto_complete_session = False
            sync_session_response = api_client.create_session(subscription['id'], auto_complete_session)

            # if sync_session_response['sync_data_available']:
            sync_session = sync_session_response['session']

            # TODO - Add 'Lobbyists' topic back to list when SyncKernel is supporting successfully. First error was AID required, then a 500 when AID was provided. Bailing on that for now.
            for topic in ['Filings', 'Clients', 'ActivityExpense', 'CampaignContributionMade', 'ContactOfPublicOfficial', 'PaymentReceived']:
                offset = 0
                page_size = 25
                logger.info(f'Synchronizing {topic}')
                session_id = sync_session['id']
                filings_qr = api_client.fetch_sync_topics(session_id, topic, page_size, offset)
                while filings_qr['hasNextPage']:
                    offset = offset + page_size
                    filings_qr = api_client.fetch_sync_topics(session_id, topic, page_size, offset)

            # Complete SyncSession
            # TODO - Lobbyist Ext is not supporting autoComplete=False, so we cannot attempt to complete a Completed session
            # logger.info('Completing sync session')
            # api_client.execute_session_command(session_id, SyncSessionCommandType.Complete.name)

            # Cancel the subscription
            logger.info('Canceling subscription')
            api_client.execute_subscription_command(subscription['id'], SyncSubscriptionCommandType.Cancel.name)

            logger.info('Synchronization lifecycle complete')
            # else:
            #     logger.info('No Sync Data Available. Nothing to retrieve')
        else:
            logger.info('The Lobbyist API system status is %s and is not Ready', sys_report.general_status)
    except Exception as ex:
        # Cancel Session on error
        if sync_session is not None:
            logger.info('Error occurred, canceling sync session')
            api_client.execute_session_command(sync_session['id'], SyncSessionCommandType.Cancel.name)
        logger.error('Error running LobbyistApiClient: %s', ex)
        sys.exit()


if __name__ == '__main__':
    main()
