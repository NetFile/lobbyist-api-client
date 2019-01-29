#!/usr/bin/python

import sys
from lobbyist_api_client import LobbyistApiClient, SyncSessionCommandType
from src import *


def write_subscription_id(id_arg):
    config[env.upper()]['SUBSCRIPTION_ID'] = id_arg
    with open('../resources/config.json', 'w') as outfile:
        json.dump(config, outfile)


def main():
    """
    This demonstrates the complete lifecycle of the Lobbyist API sync process.
    1) Create a SyncSubscription
    2) Create a SyncSession using the SyncSubscription. This will be the start of the session
    3) Synchronize Filings, Clients, Activity Expenses, Campaign Contributions Made, Contact Of Public Official, Payments Received, and Lobbyists
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

            # Create SyncSubscription
            name = 'My Lobbyist API Subscription'

            if not subscription_id:
                logger.info('Creating new subscription with name "%s"', name)
                subscription_response = api_client.create_subscription(name)
                subscription = subscription_response['subscription']

                # Create SyncSession
                logger.info('Creating sync session')
                sub_id = subscription['id']

                # Write Subscription ID to config.json file
                write_subscription_id(sub_id)
            else:
                sub_id = subscription_id

            sync_session_response = api_client.create_session(sub_id)
            sync_session = sync_session_response['session']

            # Sync all available topics
            for topic in ['Filings', 'Clients', 'ActivityExpense', 'CampaignContributionMade', 'ContactOfPublicOfficial', 'PaymentReceived', 'Lobbyists']:
                offset = 0
                page_size = 50
                logger.info(f'Synchronizing {topic}')
                session_id = sync_session['id']
                query_results = api_client.fetch_sync_topics(session_id, topic, page_size, offset)
                print_query_results(query_results)
                while query_results['hasNextPage']:
                    offset = offset + page_size
                    query_results = api_client.fetch_sync_topics(session_id, topic, page_size, offset)
                    print_query_results(query_results)

            # Complete SyncSession
            logger.info('Completing sync session')
            api_client.execute_session_command(session_id, SyncSessionCommandType.Complete.name)

            # Optionally, Cancel the subscription. Only done when no further use of subscription is required
            # logger.info('Canceling subscription')
            # api_client.execute_subscription_command(sub_id, SyncSubscriptionCommandType.Cancel.name)

            logger.info('Synchronization lifecycle complete')
        else:
            logger.info('The Lobbyist API system status is %s and is not Ready', sys_report.general_status)
    except Exception as ex:
        # Cancel Session on error
        if sync_session is not None:
            logger.info('Error occurred, canceling sync session')
            api_client.execute_session_command(sync_session['id'], SyncSessionCommandType.Cancel.name)
        logger.error('Error running LobbyistApiClient: %s', ex)
        sys.exit()


def print_query_results(query_results):
    page_number = query_results["pageNumber"]
    page_size = query_results["limit"]
    total_count = query_results["totalCount"]
    results = query_results['results']
    current_record_count = (page_number-1)*page_size if page_number > 0 else page_number*page_size
    if total_count > 0:
        logger.info(f'Retrieving {current_record_count+1} - {current_record_count+len(results)} of {total_count} records')
        logger.debug(f'Total count: {total_count}')
        logger.debug(f'Offset: {query_results["offset"]}')
        logger.debug(f'Page Size: {page_size}')
        logger.debug(f'Page Number: {page_number}')
        logger.debug(f'Has Previous Page: {query_results["hasPreviousPage"]}')
        logger.debug(f'Has Next Page: {query_results["hasNextPage"]}')
        logger.debug('No Results Available') if len(results) == 0 else logger.debug('Results')
        for result in query_results['results']:
            logger.debug(f'\t{result}')
    else:
        logger.info('No records available')


if __name__ == '__main__':
    main()
