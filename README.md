# Introduction
Bitcoin tracker is a PoC for a microservice used to track currency rates.

Meant to be run in a K8s environment.

Written using Python, Flask and SQLite. Running under Waitress WSGI Server.

## Requirements
- Python 3.6+
- Dependencies in requirements.txt

## Manual build
`docker build https://github.com/zefferno/bitcoin-tracker.git`
