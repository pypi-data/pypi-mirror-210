from typing import Dict

import os

from schema import Schema

from riptide.config.document.command import Command
from riptide.config.service.ports import get_existing_port_mapping
from riptide.db.driver.abstract import AbstractDbDriver, DbValidationError, DbImportExport
from riptide.db.environments import DbEnvironments
from riptide.engine.abstract import AbstractEngine

IMAGE_NAME = 'mysql'
# Driver is mariadb compatible
IMAGE_NAME_MARIADB = 'mariadb'
DATA_PATH = '/var/lib/mysql'
ENV_PW = 'MYSQL_ROOT_PASSWORD'
ENV_DB = 'MYSQL_DATABASE'
PORT = 3306


class MySQLDbDriver(AbstractDbDriver):
    """Database driver for 'mysql' Docker images."""

    def ask_for_import_file(self):
        return "Enter the path to the SQL file."

    def validate_service(self) -> bool:
        """
        A mysql database driver may only be used with 'mysql' or mariadb images.
        It's config must include password and database.
        """
        if self.service["image"].split(":")[0] != IMAGE_NAME and self.service["image"].split(":")[0] != IMAGE_NAME_MARIADB:
            raise DbValidationError(f"{self.service['$name']} service: A mysql database "
                                    f"driver may only be used with '{IMAGE_NAME}' or '{IMAGE_NAME_MARIADB}' images.")

        # validate schema
        return Schema({
            'password': str,
            'database': str
        }).validate(self.service['driver']['config'])

    def importt(self, engine: AbstractEngine, absolute_path_to_import_object):
        command = Command.from_dict({
            'image': self.service["image"],
            'command':
                f'mysql -h{self.service["$name"]} -uroot -p{self.service["driver"]["config"]["password"]} {self.service["driver"]["config"]["database"]} < /db_file',
            'additional_volumes': {"import": {
                'host': absolute_path_to_import_object,
                'container': '/db_file',
                'mode': 'ro'
            }}
        })
        command.validate()
        command.freeze()
        (exit_code, log) = engine.cmd_detached(self.service.get_project(), command)
        if exit_code != 0:
            raise DbImportExport(f'MySQL command failed: {log.decode("utf-8")}')

    def export(self, engine: AbstractEngine, absolute_path_to_export_target):
        name_of_file = os.path.basename(absolute_path_to_export_target)
        file_dir = os.path.abspath(os.path.join(absolute_path_to_export_target, '..'))
        command = Command.from_dict({
            'image': self.service["image"],
            'command':
                f'mysqldump -h{self.service["$name"]} -uroot -p{self.service["driver"]["config"]["password"]} {self.service["driver"]["config"]["database"]} > /db_folder/{name_of_file}',
            'additional_volumes': {"export": {
                'host': file_dir,
                'container': '/db_folder',
                'mode': 'rw'
            }}
        })
        command.validate()
        command.freeze()
        (exit_code, log) = engine.cmd_detached(self.service.get_project(), command)
        if exit_code != 0:
            raise DbImportExport(f'MySQL command failed: {log.decode("utf-8")}')

    def collect_volumes(self):
        return DbEnvironments.get_volume_configuration_for_driver(DATA_PATH, self.service)

    def collect_additional_ports(self):
        return {"mysql": {
            'title': 'MySQL Port',
            'container': PORT,
            'host_start': PORT
        }}

    def collect_environment(self):
        return {
            ENV_PW:  self.service['driver']['config']['password'],
            ENV_DB:  self.service['driver']['config']['database']
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

