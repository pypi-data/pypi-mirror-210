from typing import Dict

import os

from schema import Schema

from riptide.config.document.command import Command
from riptide.config.service.ports import get_existing_port_mapping
from riptide.db.driver.abstract import AbstractDbDriver, DbValidationError, DbImportExport
from riptide.db.environments import DbEnvironments
from riptide.engine.abstract import AbstractEngine

IMAGE_NAME = 'mongo'
# Driver is mariadb compatible
IMAGE_NAME_MARIADB = 'mongo'
DATA_PATH = '/data/db'
ENV_PW = 'MONGO_INITDB_ROOT_PASSWORD'
ENV_DB = 'MONGO_INITDB_DATABASE'
ENV_USER = 'MONGO_INITDB_ROOT_USERNAME'
PORT = 27017


class MongoDbDriver(AbstractDbDriver):
    """Database driver for 'mongo' Docker images."""

    def ask_for_import_file(self):
        return "Enter the path to the JSON file."

    def validate_service(self) -> bool:
        """
        A mongo database driver may only be used with 'mongo' images.
        It's config must include password and database.
        """
        if self.service["image"].split(":")[0] != IMAGE_NAME:
            raise DbValidationError(f"{self.service['$name']} service: A mongo database "
                                    f"driver may only be used with '{IMAGE_NAME}' images.")

        # validate schema
        return Schema({
            'password': str,
            'database': str
        }).validate(self.service['driver']['config'])

    def importt(self, engine: AbstractEngine, absolute_path_to_import_object):
        command = Command({
            'image': self.service["image"],
            'command':
                f'mongoimport '
                f'--host {self.service["$name"]} '
                f'--username root '
                f'--authenticationDatabase admin '
                f'--password {self.service["driver"]["config"]["password"]} '
                f'--db {self.service["driver"]["config"]["database"]} '
                f' --file db_file',
            'additional_volumes': {"import": {
                'host': absolute_path_to_import_object,
                'container': '/db_file',
                'mode': 'ro'
            }}
        })
        command.validate()
        (exit_code, log) = engine.cmd_detached(self.service.get_project(), command)
        if exit_code != 0:
            raise DbImportExport(f'mongoimport command failed: {log.decode("utf-8")}')

    def export(self, engine: AbstractEngine, absolute_path_to_export_target):
        name_of_file = os.path.basename(absolute_path_to_export_target)
        file_dir = os.path.abspath(os.path.join(absolute_path_to_export_target, '..'))
        command = Command({
            'image': self.service["image"],
            'command':
                f'mongoexport '
                f'--host {self.service["$name"]} '
                f'--username root '
                f'--authenticationDatabase admin '
                f'--password {self.service["driver"]["config"]["password"]} '
                f'--db {self.service["driver"]["config"]["database"]} '
                f'--out /db_folder/{name_of_file}',
            'additional_volumes': {"export": {
                'host': file_dir,
                'container': '/db_folder',
                'mode': 'rw'
            }}
        })
        command.validate()
        (exit_code, log) = engine.cmd_detached(self.service.get_project(), command)
        if exit_code != 0:
            raise DbImportExport(f'mongoexport command failed: {log.decode("utf-8")}')

    def collect_volumes(self):
        return DbEnvironments.get_volume_configuration_for_driver(DATA_PATH, self.service)

    def collect_additional_ports(self):
        return {"mysql": {
            'title': 'MongoDB Port',
            'container': PORT,
            'host_start': PORT
        }}

    def collect_environment(self):
        return {
            ENV_PW:  self.service['driver']['config']['password'],
            ENV_DB:  self.service['driver']['config']['database'],
            ENV_USER: 'root'
        }

    def collect_info(self) -> Dict[str, str]:
        port = get_existing_port_mapping(self.service.get_project(), self.service, PORT)
        if port is None:
            port = "Unknown. Start the database for the first time, to assign a port."
        return {
            'Port': port,
            'Username': 'root',
            'Password': self.service['driver']['config']['password'],
            'Main Database': self.service['driver']['config']['database']
        }
