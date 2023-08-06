from logging import Logger


class Configuration:
    logger = Logger('mysql-statement-builder')

    @staticmethod
    def set_logger(logger_instance: Logger):
        Configuration.logger = logger_instance

