# metadefender_scan
---

This program allows to scan files and folders using MetaDefender server.


## Requirements

- Python>=3.6

## Installation

### From PyPI

If you want to use `metadefender-scan` as CLI command, install latest release from PyPI:
```
python3 -m pip install metadefender-scan
```


### From source

If you want to use unreleased version, or want to contribute to the project, install `metadefender-scan` from source:
```
git clone https://github.com/mkot02/metadefender_scan.git
python3 -m pip install -e metadefender_scan
```

## Configuration

The CLI can be configured by using INI file or environment variables.
By default the location of the configuration file is `~/.config/metadefender/config.ini`.

| Config option | Environment variable | Default value | Description |
| ------------- | -------------------- | ------------- | ----------- |
| files_extension_exclude | METADEFENDER_EXCLUDE | - | Comma-separated list of files' extensions to exclude |
| files_extension_include | METADEFENDER_INCLUDE | - | Comma-separated list of files' extensions to include |
| files_recursive | METADEFENDER_RECURSIVE | False | Process files from subdirectories if specified path is directory |
| force_scan | METADEFENDER_FORCE_SCAN | False | Send file to server even if there is cached result for this file |
| log_level | METADEFENDER_LOG_LEVEL | 0 | Logging level (see [Logging](#logging) section) |
| metadefender_server | METADEFENDER_SERVER | - | URL of MetaDefender service |
| metadefender_user | METADEFENDER_USER | - | Username to authenticate in MetaDefender |
| (1) | METADEFENDER_PASSWORD | - | User's password to authenticate in MetaDefender |
| report_format | METADEFENDER_REPORT | yaml | Format of report with scanning results (yaml, json) |
| verify_ssl | METADEFENDER_VERIFY_SSL | True | Enable SSL verification when establishing HTTPS session |
| workers_number | METADEFENDER_WORKERS | 1 | Number of concurrent jobs |

> (1) Password cannot be specified in configuration file.


Sample configuration file:

```ini
[metadefender]
files_extension_exclude = log
files_recursive = True
force_scan = False
log_level = 3
metadefender_server = https://metadefender.example.com
report_format = yaml
verify_ssl = false
workers_number = 2
```


## CLI Arguments

Command short | Command long | Description | Default |
| :-- | :-- | :-- | :-- |
| -r | --recursive | Scan files from subdirectories if specified file is a directory itself | False |
| -i | --extension-include | Specify comma-separated list of file extensions. Only files with specified extensions will be scanned | |
| -e | --extension-exclude | Specify comma-separated list of file extensions. Files with specified extensions will not be scanned | |
| -o | --output | Specify file which scanning results will be saved to | |
| -f | --format | Output format for scanning report (json/yaml) | yaml |
| -s | --server | Specify URL of MetaDefender server | |
| -u | --user | Username to authenticate in MetaDefender | |
| -p | --password | User's password to authenticate in MetaDefender | |
| -k | --ignore-ssl-errors | Ignore SSL certificate verification errors | |
|    | --force | Send file to server even if there is cached result for this file | False |
| -c | --config | Specify path to custom configuration file (see [Configuration](#configuration)) | |
| -j | --jobs | Specify how many concurrent jobs should be started. Works only if scanning directory | 1 |
| -v | --verbose | Verbose mode (see [Logging](#logging)) | False |
| -h | --help | Print help message | |


## Logging

See table below for information what types of log messages will be displayed for each log level.

| Log level | CLI option | Description |
| --------- | ---------- | ----------- |
| 0 | | All log messages suppressed |
| 1 | -v | Show only error messages |
| 2 | -vv | Show additional warning messages |
| 3 | -vvv | Show additional info messages |
| 4 | -vvvv | Show all debug information |


## Exit codes

| Exit code | Description |
| --------- | ----------- |
| 0 | Scanning successful: no thread detected |
| 1 | Scanning failed: server returned scanning error |
| 2 | Scanning failed: file not found |
| 3 | Scanning failed: failed to connect to the server |
| 4 | Scanning failed: application error |


## Examples

Show help:
```
metadefender_scan -h
```

General usage:
```
metadefender_scan [OPTIONS] [FILES]
```

Scan files **test_file1.exe**, **test_file2.exe** and all files in test_dir:
```
metadefender_scan -s http://metadefender.example.com test_file1.exe test_file2.exe test_dir
```

Scan files from **test_dir** and all subdirectories, without files with extension: __*.o__, __*.pyc__, __*.tmp__, __*.txt__, __*.doc__:
```
metadefender_scan -s http://metadefender.example.com -r -e o,pyc,tmp,txt,doc test_dir
```

Scan only __*.exe__ files from **test_dir** directory and all subdirectories:
```
metadefender_scan -s http://metadefender.example.com -r -i exe test_dir
```

Scan files **test_file1.exe**, **test_file2.exe** and save output to file **results.html**:
```
metadefender_scan -s http://metadefender.example.com -o results.html test_file1.exe test_file2.exe test_dir
```


## TODO

- Add batch processing
- Add processing of files secured with passwords
- Add tests in pipeline


## Author

mkot02
