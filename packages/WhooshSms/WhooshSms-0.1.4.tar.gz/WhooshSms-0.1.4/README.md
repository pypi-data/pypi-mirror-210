# whoosh-python
## Versions

`whoosh-python` uses a modified version of [Semantic Versioning](https://semver.org) for all changes. [See this document](VERSIONS.md) for details.

### Supported Python Versions

This library supports the following Python implementations:

- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11

## Installation

Install from PyPi using [pip](https://pip.pypa.io/en/latest/), a
package manager for Python.

```shell
pip3 install WhooshSms
```

If pip install fails on Windows, check the path length of the directory. If it is greater 260 characters then enable [Long Paths](https://docs.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation) or choose other shorter location.

Don't have pip installed? Try installing it, by running this from the command
line:

```shell
curl https://bootstrap.pypa.io/get-pip.py | python
```

Or, you can [download the source code
(ZIP)](https://github.com/totogi/whoosh-python/zipball/main 'whoosh-python
source code') for `whoosh-python`, and then run:

```shell
python3 setup.py install
```

> **Info**
> If the command line gives you an error message that says Permission Denied, try running the above commands with `sudo` (e.g., `sudo pip3 install WhooshSms`).

### Test your installation

Try sending yourself an SMS message. Save the following code sample to your computer with a text editor. Be sure to update the `account_sid`, `auth_token`, and `from_` phone number with values from your [Whoosh account](https://console.whoosh.totogidemos.com). The `to` phone number will be your own mobile phone.
