# TwOSINT - Twitter OSINT tool

### Providing API Bearer Token
The API bearer token can be provided with any of the following ways:

Command line argument:
```bash
$ python3 TwOSINT.py -t <bearer_token>
```
Environment variable:
```bash
$ export BEARER_TOKEN=<bearer_token>    # Linux
$ set BEARER_TOKEN=<bearer_token>       # Windows
```
bearer_token.txt file:
```
bearer_token=<bearer_token>
```
As input when prompted to enter the bearer token

### Running Tests
Tests can be ran with the commnd:
```bash
$ python3 -m pytest
```