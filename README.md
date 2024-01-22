# ArduinoResponse

## Description

A net work monitor based on ardunio and python.
(Based on ESP8266 and a public server)

## Installation

flash the arduino code to the ESP8266 and run the python script on a server.

```bash
pip install -r requirements.txt
```

## Usage/Examples

```shell
uvicorn main.py:app --reload
```

## API Reference

/status - for submitting data
/ - for viewing data
/ws - for viewing data in real time

## Contributing

EE

## License

CC