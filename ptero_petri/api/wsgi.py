from ptero_petri.api import application
from ptero_common.logging_configuration import configure_logging
import argparse
import logging

app = application.create_app()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--debug', action='store_true', default=False)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    configure_logging(level_env_var='PTERO_PETRI_LOG_LEVEL',
            time_env_var='PTERO_PETRI_LOG_TIME')
    logging.getLogger('pika').setLevel('INFO')
    app.run(port=args.port, debug=args.debug)
