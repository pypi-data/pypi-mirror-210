import configparser
import hashlib
import json
import os
from typing import Generator, Iterable

import yaml

from metadefender.api import MetadefenderApi, MetadefenderApiException
from metadefender.logging import logger


class MetadefenderScanner:
    def __init__(
        self,
        server: str,
        user: str = None,
        password: str = None,
        force: bool = False,
        verify_ssl: bool = True,
    ) -> None:
        """Class that implements scanning using MetaDefender Core service.

        Args:
            server (str): URL of a MetaDefender server.
            user (str, optional): Username to authenticate in MetaDefender. Defaults to None.
            password (str, optional): User's password to authenticate in MetaDefender. Defaults to None.
            force (bool, optional): upload files for scanning even if they were scanned already. Defaults to False.
            verify_ssl (bool, optional): Enable SSL verification for HTTP requests. Defaults to True.

        Raises:
            RuntimeError: when connection to MetaDefender API failed.
        """
        self.force = bool(force)
        self.result_list = []

        try:
            self.server_api = MetadefenderApi(server, verify_ssl)
            if user is not None and password is not None:
                self.server_api.login(user, password)
            elif user is None and password is None:
                pass
            else:
                raise RuntimeError("Both username and password must be provided at the same time")
        except Exception as e:
            raise RuntimeError("Failed to connect to Metadefender Server: {}".format(str(e)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.server_api.logout()

    def __del__(self):
        self.server_api.logout()

    def _calculate_file_hash(self, filename: str, hash_type: str = "MD5") -> str:
        """Calculates checksum of specified file using selected hashing algorithm.

        Args:
            filename (str): path to the file on local system
            hash_type (str, optional): hashing algorithm to use. Possible values: MD5, SHA1, SHA256. Defaults to "MD5".

        Returns:
            str: hash of the file converted to HEX
        """
        HASH_FUNCTIONS = {
            "MD5": hashlib.md5,
            "SHA1": hashlib.sha1,
            "SHA256": hashlib.sha256,
        }
        hash_o = HASH_FUNCTIONS.get(hash_type.upper(), hashlib.md5)()

        with open(filename, "rb") as fd:
            while True:
                chunk = fd.read(1000000)
                if len(chunk):
                    hash_o.update(chunk)
                else:
                    return hash_o.hexdigest()

    def scan_file(self, filename: str) -> tuple:
        """Checks whether file was already scanned and depending on 'force' parameter from class constructor
        upload file for scanning.

        Args:
            filename (str): name of the file specified for scanning

        Returns:
            tuple: name of the file and scanning result
        """
        file_hash = self._calculate_file_hash(filename)

        try:
            logger.info("Checking scanning status for file '%s'", filename)
            result = self.server_api.get_hash_details(file_hash)
        except (ValueError, MetadefenderApiException) as e:
            logger.error("Failed to get scan details for file '%s': %s", filename, str(e))
            result = None
        except Exception as e:
            logger.error("Failed to get scan details for file '%s': %s", filename, str(e))
            result = None
        else:
            logger.info("Fetched scanning results for file '%s'", filename)

        # Check if result result is proper and doesn't contain Not Found
        # of if force mode is set
        if result is None:
            logger.warning("Skipping scanning for file '%s' due to previous error", filename)
            return (filename, result)

        if "Not Found" not in result and not self.force:
            logger.debug(
                "Skipping scanning for already scanned file '%s' with force mode disabled",
                filename,
            )
            return (filename, result)
        elif "Not Found" not in result and self.force:
            logger.warning(
                "Continuing scanning for already scanned file '%s' with force mode enabled",
                filename,
            )

        try:
            logger.info("Scanning file '%s'", filename)
            data_id = self.server_api.upload_file(filename)
            self.server_api.wait_for_scan(json.loads(data_id)["data_id"])
        except (ValueError, MetadefenderApiException) as e:
            logger.error("Failed to scan file '%s': %s", filename, str(e))
            result = None
        except Exception as e:
            logger.error("Failed to get scan details for file '%s': %s", filename, str(e))
            result = None
        else:
            logger.debug("Successfully scanned file '%s'", filename)
            result = self.server_api.get_hash_details(file_hash)

        return (filename, result)

    def map(self, file_iter: Iterable) -> Generator:
        """Returns generator over results of scanned files.

        Args:
            file_iter (Iterable): iterable with names of files to scan

        Yields:
            Generator: generator which iterates over results of scanning
        """
        return (self.scan_file(file_to_process) for file_to_process in file_iter)


class MetadefenderResultParser:
    def __init__(self) -> None:
        """This class is intended to parse and return results of MetaDefender API scanning in desired format"""
        self.result_map = dict()
        self.result_map["results"] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return

    def update(self, json_string: str) -> None:
        """Update the result-object with new result from MetaDefender API.

        Args:
            json_string (str): string with JSON response from MetaDefender API
        """
        self.result_map["results"].append(json.loads(json_string))

    def is_threat_detected(self) -> bool:
        """Returns status of the scan.
        If any of the scanned files has been detected as infected,
        this function returns 'True'.

        Returns:
            bool: threat status
        """
        return False

    def dump_json(self) -> str:
        """Dump results to JSON format.

        Returns:
            str: string with results dumped to YAML
        """
        return json.dumps(self.result_map, indent=4)

    def dump_yaml(self) -> str:
        """Dump results to YAML format.

        Returns:
            str: string with results dumped to YAML
        """
        return yaml.safe_dump(self.result_map)


class MetadefenderConfig:
    __env_opt_exclude = "METADEFENDER_EXCLUDE"
    __env_opt_include = "METADEFENDER_INCLUDE"
    __env_opt_recursive = "METADEFENDER_RECURSIVE"
    __env_opt_log_level = "METADEFENDER_LOG_LEVEL"
    __env_opt_server = "METADEFENDER_SERVER"
    __env_opt_user = "METADEFENDER_USER"
    __env_opt_password = "METADEFENDER_PASSWORD"
    __env_opt_ssl = "METADEFENDER_VERIFY_SSL"
    __env_opt_force_scan = "METADEFENDER_FORCE_SCAN"
    __env_opt_report = "METADEFENDER_REPORT"
    __env_opt_workers = "METADEFENDER_WORKERS"
    __ini_section = "metadefender"
    __ini_opt_exclude = "files_extension_exclude"
    __ini_opt_include = "files_extension_include"
    __ini_opt_recursive = "files_recursive"
    __ini_opt_log_level = "log_level"
    __ini_opt_server = "metadefender_server"
    __ini_opt_user = "metadefender_user"
    __ini_opt_password = "metadefender_password"
    __ini_opt_ssl = "verify_ssl"
    __ini_opt_force_scan = "force_scan"
    __ini_opt_report = "report_format"
    __ini_opt_workers = "workers_number"

    def __init__(self) -> None:
        # Initialize variables for settings with default values
        self._config = dict()
        self._config[self.__ini_opt_exclude] = None
        self._config[self.__ini_opt_include] = None
        self._config[self.__ini_opt_recursive] = False
        self._config[self.__ini_opt_log_level] = 0
        self._config[self.__ini_opt_server] = None
        self._config[self.__ini_opt_user] = None
        self._config[self.__ini_opt_password] = None
        self._config[self.__ini_opt_ssl] = True
        self._config[self.__ini_opt_force_scan] = False
        self._config[self.__ini_opt_report] = "yaml"
        self._config[self.__ini_opt_workers] = 1

    def load_env(self) -> None:
        """Read configuration from environment variables."""
        logger.debug("Loading configuration from environment variables")

        _env_files_exclude = os.getenv(self.__env_opt_exclude)
        if _env_files_exclude is not None:
            logger.debug(f"Detected '{self.__env_opt_exclude}' setting with value '{_env_files_exclude}'")
            self.files_extension_exclude = _env_files_exclude

        _env_files_include = os.getenv(self.__env_opt_include)
        if _env_files_include is not None:
            logger.debug(f"Detected '{self.__env_opt_include}' setting with value '{_env_files_include}'")
            self.files_extension_include = _env_files_include

        _env_files_recursive = os.getenv(self.__env_opt_recursive)
        if _env_files_recursive is not None:
            logger.debug(f"Detected '{self.__env_opt_recursive}' setting with value '{_env_files_recursive}'")
            self.files_recursive = _env_files_recursive

        _env_log_level = os.getenv(self.__env_opt_log_level)
        if _env_log_level is not None:
            logger.debug(f"Detected '{self.__env_opt_log_level}' setting with value '{_env_log_level}'")
            self.log_level = int(_env_log_level)

        _env_metadefender_server = os.getenv(self.__env_opt_server)
        if _env_metadefender_server is not None:
            logger.debug(f"Detected '{self.__env_opt_server}' setting with value '{_env_metadefender_server}'")
            self.metadefender_server = _env_metadefender_server

        _env_metadefender_user = os.getenv(self.__env_opt_user)
        if _env_metadefender_user is not None:
            logger.debug(f"Detected '{self.__env_opt_user}' setting with value '{_env_metadefender_user}'")
            self.metadefender_user = _env_metadefender_user

        _env_metadefender_password = os.getenv(self.__env_opt_password)
        if _env_metadefender_password is not None:
            logger.debug(f"Detected '{self.__env_opt_password}' setting with value '{_env_metadefender_password}'")
            self.metadefender_password = _env_metadefender_password

        _env_metadefender_ssl = os.getenv(self.__env_opt_ssl)
        if _env_metadefender_ssl is not None:
            logger.debug(f"Detected '{self.__env_opt_ssl}' setting with value '{_env_metadefender_ssl}'")
            self.metadefender_ssl = _env_metadefender_ssl

        _env_metadefender_force = os.getenv(self.__env_opt_force_scan)
        if _env_metadefender_force is not None:
            logger.debug(f"Detected '{self.__env_opt_force_scan}' setting with value '{_env_metadefender_force}'")
            self.force_scan = _env_metadefender_force

        _env_report_format = os.getenv(self.__env_opt_report)
        if _env_report_format is not None:
            logger.debug(f"Detected '{self.__env_opt_report}' setting with value '{_env_report_format}'")
            self.report_format = _env_report_format

        _env_workers_number = os.getenv(self.__env_opt_workers)
        if _env_workers_number is not None:
            logger.debug(f"Detected '{self.__env_opt_workers}' setting with value '{_env_workers_number}'")
            self.workers_number = int(_env_workers_number)

    def load_file(self, config_file: str = None) -> None:
        """Read configuration from file. When file is not specified, teh function tries to load
        default configuration file if exists (~/.config/metadefender/config.ini).

        Args:
            config_file (str): full path to configuration file in ini format. Defaults to None.

        Raises:
            RuntimeError: when file doesn't exist or cannot be parsed.
        """
        if config_file is None:
            _config_base = os.path.expanduser("~")
            _config_path = os.path.join(_config_base, ".config", "metadefender", "config.ini")
            if os.path.exists(_config_path):
                logger.debug(f"Using default configuration file '{_config_path}'")
            else:
                # When file doesn't exits, exit function without doing anything,
                # as this configuration file is optional.
                return
        else:
            _config_path = config_file

        _config = configparser.ConfigParser()
        try:
            logger.debug(f"Reading configuration from '{_config_path}'")
            with open(_config_path, "rb") as fd:
                _config.read_string(fd.read().decode())
        except FileNotFoundError:
            raise RuntimeError(f"File '{_config_path}' doesn't exist")

        if not _config.has_section(self.__ini_section):
            raise RuntimeError("Config file doesn't have 'metadefender' section")

        if _config.has_option(self.__ini_section, self.__ini_opt_exclude):
            _value = _config.get(self.__ini_section, self.__ini_opt_exclude)
            logger.debug(f"Detected '{self.__ini_opt_exclude}' setting with value '{_value}'")
            self.files_extension_exclude = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_include):
            _value = _config.get(self.__ini_section, self.__ini_opt_include)
            logger.debug(f"Detected '{self.__ini_opt_include}' setting with value '{_value}'")
            self.files_extension_include = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_recursive):
            _value = _config.get(self.__ini_section, self.__ini_opt_recursive)
            logger.debug(f"Detected '{self.__ini_opt_recursive}' setting with value '{_value}'")
            self.files_recursive = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_log_level):
            _value = _config.get(self.__ini_section, self.__ini_opt_log_level)
            logger.debug(f"Detected '{self.__ini_opt_log_level}' setting with value '{_value}'")
            self.log_level = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_server):
            _value = _config.get(self.__ini_section, self.__ini_opt_server)
            logger.debug(f"Detected '{self.__ini_opt_server}' setting with value '{_value}'")
            self.metadefender_server = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_user):
            _value = _config.get(self.__ini_section, self.__ini_opt_user)
            logger.debug(f"Detected '{self.__ini_opt_user}' setting with value '{_value}'")
            self.metadefender_user = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_ssl):
            _value = _config.get(self.__ini_section, self.__ini_opt_ssl)
            logger.debug(f"Detected '{self.__ini_opt_ssl}' setting with value '{_value}'")
            self.metadefender_ssl = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_force_scan):
            _value = _config.get(self.__ini_section, self.__ini_opt_force_scan)
            logger.debug(f"Detected '{self.__ini_opt_force_scan}' setting with value '{_value}'")
            self.force_scan = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_report):
            _value = _config.get(self.__ini_section, self.__ini_opt_report)
            logger.debug(f"Detected '{self.__ini_opt_report}' setting with value '{_value}'")
            self.report_format = _value

        if _config.has_option(self.__ini_section, self.__ini_opt_workers):
            _value = _config.get(self.__ini_section, self.__ini_opt_workers)
            logger.debug(f"Detected '{self.__ini_opt_workers}' setting with value '{_value}'")
            self.workers_number = _value

    def dump_json(self) -> str:
        """Dump configuration to JSON format.

        Returns:
            str: string with config dumped to YAML
        """
        return json.dumps(self._config, indent=4)

    def dump_yaml(self) -> str:
        """Dump configuration to YAML format.

        Returns:
            str: string with config dumped to YAML
        """
        return yaml.safe_dump(self._config)

    @property
    def files_extension_exclude(self):
        return self._config[self.__ini_opt_exclude]

    @files_extension_exclude.setter
    def files_extension_exclude(self, value):
        self._config[self.__ini_opt_exclude] = value

    @property
    def files_extension_include(self):
        return self._config[self.__ini_opt_include]

    @files_extension_include.setter
    def files_extension_include(self, value):
        self._config[self.__ini_opt_include] = value

    @property
    def files_recursive(self):
        return self._config[self.__ini_opt_recursive]

    @files_recursive.setter
    def files_recursive(self, value):
        if value in [1, "1", "TRUE", "true", "True"]:
            self._config[self.__ini_opt_recursive] = True
        elif value in [0, "0", "FALSE", "false", "False"]:
            self._config[self.__ini_opt_recursive] = False
        elif value is not None:
            raise ValueError(f"Invalid value for files_recursive: {value}")

    @property
    def log_level(self):
        return self._config[self.__ini_opt_log_level]

    @log_level.setter
    def log_level(self, value):
        _value = int(value)
        if _value < 0 or _value > 4:
            raise ValueError(f"Invalid value for log_level: {_value}")
        else:
            self._config[self.__ini_opt_log_level] = _value

    @property
    def metadefender_server(self):
        return self._config[self.__ini_opt_server]

    @metadefender_server.setter
    def metadefender_server(self, value):
        self._config[self.__ini_opt_server] = value

    @property
    def metadefender_user(self):
        return self._config[self.__ini_opt_user]

    @metadefender_user.setter
    def metadefender_user(self, value):
        self._config[self.__ini_opt_user] = value

    @property
    def metadefender_password(self):
        return self._config[self.__ini_opt_password]

    @metadefender_password.setter
    def metadefender_password(self, value):
        self._config[self.__ini_opt_password] = value

    @property
    def metadefender_ssl(self):
        return self._config[self.__ini_opt_ssl]

    @metadefender_ssl.setter
    def metadefender_ssl(self, value):
        if value in [1, "1", "TRUE", "true", "True"]:
            self._config[self.__ini_opt_ssl] = True
        elif value in [0, "0", "FALSE", "false", "False"]:
            self._config[self.__ini_opt_ssl] = False
        elif value is not None:
            raise ValueError(f"Invalid value for metadefender_ssl: {value}")

    @property
    def force_scan(self):
        return self._config[self.__ini_opt_force_scan]

    @force_scan.setter
    def force_scan(self, value):
        if value in [1, "1", "TRUE", "true", "True"]:
            self._config[self.__ini_opt_force_scan] = True
        elif value in [0, "0", "FALSE", "false", "False"]:
            self._config[self.__ini_opt_force_scan] = False
        elif value is not None:
            raise ValueError(f"Invalid value for force_scan: {value}")

    @property
    def report_format(self):
        return self._config[self.__ini_opt_report]

    @report_format.setter
    def report_format(self, value):
        if value in ["json", "yaml"]:
            self._config[self.__ini_opt_report] = value
        else:
            raise ValueError(f"Invalid value for report_format: {value}")

    @property
    def workers_number(self):
        return self._config[self.__ini_opt_workers]

    @workers_number.setter
    def workers_number(self, value):
        _value = int(value)
        if _value < 1:
            raise ValueError(f"Invalid value for workers_number: {_value}")
        else:
            self._config[self.__ini_opt_workers] = _value
