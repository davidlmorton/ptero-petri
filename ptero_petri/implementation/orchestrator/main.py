from ptero_petri.implementation import exit_codes
from ptero_petri.implementation.configuration.inject.initialize import initialize_injector
from ptero_petri.implementation.orchestrator.command import OrchestratorCommand
from ptero_petri.implementation.util import signal_handlers
from ptero_common.logging_configuration import configure_logging
from twisted.internet import reactor
import logging
import os
import pika
import sys
import traceback


LOG = logging.getLogger(__name__)


def main():
    try:
        signal_handlers.setup_standard_signal_handlers()

        exit_code = naked_main()

    except SystemExit as e:
        exit_code = e.code
    except:
        sys.stderr.write('Unhandled exception:\n')
        traceback.print_exc()
        exit_code = exit_codes.UNKNOWN_ERROR

    return exit_code


def naked_main():
    configure_logging(level_env_var='PTERO_PETRI_LOG_LEVEL',
            time_env_var='PTERO_PETRI_LOG_TIME')
    logging.getLogger('ptero_petri.implementation.brokers').setLevel(
            os.environ.get('PTERO_PETRI_BROKER_LOG_LEVEL', 'INFO'))
    logging.getLogger('pika').setLevel('INFO')

    injector = initialize_injector()

    # XXX Hack to get the command to show up in the rabbitmq admin interface
    pika.connection.PRODUCT = 'orchestrator'

    try:
        LOG.info('Instantiating orchestrator comand...')
        command = injector.get(OrchestratorCommand)
    except:
        LOG.exception('Could not instantiate command object.')
        return exit_codes.EXECUTE_ERROR

    reactor.run()

    LOG.info('Orchestrator exiting...')
    return exit_codes.EXECUTE_FAILURE


if __name__ == '__main__':
    main()
