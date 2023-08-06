import argparse
import logging
from logging.handlers import TimedRotatingFileHandler

from cenao.app import Application
from cenao.config import Config


class ApplicationRunner:
    app: Application

    def __init__(self, app: Application):
        self.app = app

    def run(self):
        parser = argparse.ArgumentParser(description='Run a cenao application')
        parser.add_argument('-c', '--config', help='Application configuration', default=None)
        parser.add_argument(
            '-e', '--env-prefix',
            help='Prefix of environment variables which would redefine config values',
            default='APP',
        )
        args = parser.parse_args()

        config = Config(args.config)
        config.process_env(args.env_prefix)

        self._init_logger(config)
        self.app.init(config)
        self.app.run()

    def _init_logger(self, config):
        config = config.get('logging', {})
        fmt = config.get('format', '%(asctime)s [%(levelname)s] [%(name)s] %(message)s')
        level = config.get('level', 'INFO')
        file = config.get('file', f'{self.app.NAME.lower()}.log')
        rotation_when = config.get('rotation_when', 'h')
        rotation_interval = config.get('rotation_interval', 1)
        rotation_backups = config.get('rotation_backups', 6)
        to_file = config.get('to_file', False)
        to_stdout = config.get('to_stdout', True)

        logger = logging.root
        formatter = logging.Formatter(fmt)

        if to_file:
            file_handler = TimedRotatingFileHandler(
                file,
                when=rotation_when,
                interval=rotation_interval,
                backupCount=rotation_backups,
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        if to_stdout:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(level)
