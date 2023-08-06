from testgear_cli.parser import Parser

from testgear_cli.apiclient import ApiClient
from testgear_cli.args_parser import ArgsParser
from testgear_cli.configurator import Configurator
from testgear_cli.importer import Importer
from testgear_cli.logger import Logger
from testgear_cli.models.mode import Mode
from testgear_cli.service import Service


def console_main():
    arg_parser = ArgsParser()
    config = Configurator(arg_parser)

    Logger.register_logger(config.is_debug())

    api_client = ApiClient(config.get_url(), config.get_private_token())
    parser = Parser(config)
    importer = Importer(api_client, config)
    service = Service(config, api_client, parser, importer)

    mode = config.get_mode()
    if mode is Mode.IMPORT:
        service.import_results()

    elif mode is Mode.CREATE_TEST_RUN:
        service.create_testrun()

    elif mode is Mode.FINISHED_TEST_RUN:
        service.finished_testrun()

    elif mode is Mode.UPLOAD:
        service.upload_results()


if __name__ == "__main__":
    console_main()
