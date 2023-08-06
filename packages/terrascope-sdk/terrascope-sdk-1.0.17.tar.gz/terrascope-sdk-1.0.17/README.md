# TerraScope SDK

## Description

The TerraScope Platform is a collection of tools to analyze sensor data over space and time. The TerraScope SDK 
(software development kit) is a Python package that simplifies users' interaction with the TerraScope Platform API.

## Installation

[Readme: Installation](https://terrascope.readme.io/docs/installation-1)

## Usage

TerraScope SDK is designed to simplify access to all the [terrascope-api](https://pypi.org/project/terrascope-api/) calls
that are available. Ensure that you have the correct terrascope-api package installed.

Each API uses a client object which requires the following env variables to be set:

```shell
TERRASCOPE_API_HOST=terrascope-api1.orbitalinsight.com
TERRASCOPE_API_TOKEN=<TerraScope API Token>
TERRASCOPE_TIMEOUT=<Int timeout in seconds> defaults to 60 seconds
```

You will always want to ensure that you have the correct terrascope-sdk version installed. The latest can be found here:
https://pypi.org/project/terrascope-sdk/

To manually build a local version of the terrascope-sdk (for example, if you are making changes and want to test):
1. Update the version specified in the `pyproject.toml` file, e.g. `version = "1.0.6-test"`
2. Execute from the top-level terrascope_sdk folder: `python3 -m build`
3. `cd dist/`
4. `pip3 install terrascope_sdk-1.0.6-test-py3-none-any.whl` (this file name may be different based on the version specified)

## Authors and acknowledgment

Orbital Insight

## License

[LICENSE](LICENSE)

