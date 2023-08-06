
# AeroApi Python

Python wrapper for the FlightAware's AeroAPI

## Description

AeroAPI (formerly FlightXML) is FlightAware's live flight data API that provides powerful, reliable information about real-time and historical flight information. This Python wrapper allows for easier interaction with the AeroAPI from Python applications.

## FlightAware AeroAPI Reference
[AeroAPI](https://flightaware.com/aeroapi)

## Installation

```bash
pip install aeroapi-python
```
    
### Using test pypi, install with this command.
```bash
pip install --index-url https://pypi.org/simple/ --extra-index-url https://test.pypi.org/simple/ aeroapi-python
```

## Usage

```python
from aeroapi_python import AeroApi

# initialize with your AeroAPI username and API Key
aero_api = AeroAPI('your-api-key')
```

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Authors

- [@derens99](https://www.github.com/derens99)