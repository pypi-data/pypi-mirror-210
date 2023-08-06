from metadefender.app import (
    MetadefenderConfig,
    MetadefenderResultParser,
    MetadefenderScanner,
)
from metadefender.logging import logger, set_logger

__version = "0.2.0-dev"


EXIT_STATUS = {
    "SUCCESS": 0,
    "SERVER_ERROR": 1,
    "FILE_NOT_FOUND": 2,
    "CONNECTION_ERROR": 3,
    "APP_ERROR": 4,
}


def build_scan_list(files, includes=None, excludes=None, recursive=None):
    import os

    files = files if isinstance(files, list) else [files]
    logger.debug(f"Building list of files to scan from: {files}")

    result_list = []
    for fil in files:
        # Discard files which don't exists
        if not os.path.exists(fil):
            continue

        if os.path.isdir(fil):
            # Extend result list with file lists (2nd element of tuple)
            # of this this directory and all subdirectories
            for walk_step in os.walk(fil):
                dir_file_list = [os.path.join(walk_step[0], f) for f in walk_step[2]]
                result_list.extend(dir_file_list)

                # Break after first iteration if recursive flag is not set to
                # list only files in directory not subdirectories
                if fil == walk_step[0] and not recursive:
                    break
        else:
            result_list.append(fil)

    # Apply filters and return
    if (includes not in [None, ""]) and (excludes not in [None, ""]):
        raise ValueError("Includes and excludes cannot be specified at the same time")
    elif includes is not None:
        ext_list = tuple(["." + ext for ext in includes.split(",")])
        return [os.path.abspath(f) for f in result_list if f.endswith(ext_list)]
    elif excludes is not None:
        ext_list = tuple(["." + ext for ext in excludes.split(",")])
        return [os.path.abspath(f) for f in result_list if not f.endswith(ext_list)]
    else:
        return result_list


def main():
    import argparse
    import getpass
    import multiprocessing.dummy as multiprocessing

    parser = argparse.ArgumentParser(prog="metadefender_scan", add_help=False)
    group_file = parser.add_argument_group(title="File(s) settings")
    group_file.add_argument("files", nargs="+")
    group_file.add_argument(
        "-r",
        "--recursive",
        help="Scan files from subdirectories if specified file is a directory itself",
        action="store_true",
    )
    group_filter = group_file.add_mutually_exclusive_group()
    group_filter.add_argument(
        "-i",
        "--extension-include",
        dest="includes",
        help="Specify comma-separated list of file extensions. Only files with specified extensions will be scanned",
    )
    group_filter.add_argument(
        "-e",
        "--extension-exclude",
        dest="excludes",
        help="Specify comma-separated list of file extensions. Files with specified extensions will not be scanned",
    )
    group_report = parser.add_argument_group(title="Report settings")
    group_report.add_argument(
        "-o",
        "--output",
        help="Specify file which scanning results will be saved to",
    )
    group_report.add_argument(
        "-f",
        "--format",
        choices=["json", "yaml"],
        help="Output format for scanning report",
    )
    group_server = parser.add_argument_group(title="Server settings")
    group_server.add_argument(
        "-s",
        "--server",
        help="Specify URL of MetaDefender server",
    )
    group_server.add_argument(
        "-u",
        "--user",
        help="Username to authenticate in MetaDefender server",
    )
    group_server.add_argument(
        "-p",
        "--password",
        help="User's password to authenticate in MetaDefender server",
    )
    group_server.add_argument(
        "-k",
        "--ignore-ssl-errors",
        help="Ignore SSL certificate verification errors",
        action="store_false",
    )
    group_server.add_argument(
        "--force",
        action="store_true",
        help="Send file to server even if there is cached result for this file",
    )
    group_other = parser.add_argument_group(title="Other settings")
    group_other.add_argument(
        "-c",
        "--config",
        help="Specify path to custom configuration file",
    )
    group_other.add_argument(
        "-j",
        "--jobs",
        type=int,
        help="Specify how many concurrent jobs should be started. Works only if scanning directory",
    )
    group_other.add_argument("-h", "--help", help="Print this help message", action="help")
    group_other.add_argument("-v", "--verbose", help="Verbose mode (max -vvvv)", action="count", default=0)
    cli_args = parser.parse_args()

    # Setup logger
    set_logger(cli_args.verbose)

    # Setup configuration
    try:
        config = MetadefenderConfig()
        config.load_file(cli_args.config)
        config.load_env()
    except RuntimeError as e:
        logger.critical(str(e))
        exit(EXIT_STATUS["APP_ERROR"])

    if cli_args.excludes:
        config.files_extension_exclude = cli_args.excludes

    if cli_args.includes:
        config.files_extension_include = cli_args.includes

    if cli_args.server:
        config.metadefender_server = cli_args.server

    if cli_args.user:
        config.metadefender_user = cli_args.user

    if cli_args.password:
        config.metadefender_password = cli_args.password

    if config.metadefender_user and not config.metadefender_password:
        config.metadefender_password = getpass.getpass()

    if cli_args.format:
        config.report_format = cli_args.format

    if cli_args.jobs:
        config.workers_number = cli_args.jobs

    config.files_recursive = config.files_recursive or cli_args.recursive
    config.metadefender_ssl = config.metadefender_ssl and cli_args.ignore_ssl_errors
    config.force_scan = config.force_scan or cli_args.force

    # Update log level for logger if not specified in args
    if not cli_args.verbose:
        set_logger(config.log_level)

    logger.debug(f"Final configuration options:\n{config.dump_yaml()}")

    # Parse list of input files
    logger.info("Creating list of files to scan")
    file_list = build_scan_list(
        cli_args.files,
        config.files_extension_include,
        config.files_extension_exclude,
        config.files_recursive,
    )

    if len(file_list):
        logger.info("Discovered %d files to scan", len(file_list))
        for fil in file_list:
            logger.debug("File %s will be scanned", fil)
    else:
        logger.error("No files to scan found")
        exit(EXIT_STATUS["FILE_NOT_FOUND"])

    # Create objects
    try:
        scanner = MetadefenderScanner(
            server=config.metadefender_server,
            user=config.metadefender_user,
            password=config.metadefender_password,
            verify_ssl=config.metadefender_ssl,
            force=config.force_scan,
        )
    except RuntimeError as e:
        logger.error(str(e))
        exit(EXIT_STATUS["CONNECTION_ERROR"])

    result_parser = MetadefenderResultParser()
    process_pool = multiprocessing.Pool(processes=config.workers_number)

    result_map = process_pool.map(scanner.scan_file, file_list)

    # Update result_parser with results
    for filename, result in result_map:
        if result is not None:
            result_parser.update(result)
        else:
            logger.warning("Ignoring empty result for file '%s'", filename)
    else:
        logger.debug(f"Creating scanning report in '{config.report_format}' format")
        if config.report_format == "yaml":
            results = result_parser.dump_yaml()
        elif config.report_format == "json":
            results = result_parser.dump_json()

    # Deal with the results
    if cli_args.output:
        logger.info(f"Saving scanning report to file: {cli_args.output}")
        with open(cli_args.output, "w") as fd:
            fd.write(results)
    else:
        logger.info("Scanning report:\n")
        print(results)

    exit(EXIT_STATUS["SUCCESS"])


if __name__ == "__main__":
    main()
