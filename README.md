# Introduction
Bitcoin tracker is a tiny web-based microservice used to track currency rates.

Meant to be used in K8s environment as a PoC.

Written using Python, Flask and SQLite. Running under Waitress WSGI Server.

## Requirements
- Python 3.6+
- Dependencies in requirements.txt

## Manual build
`docker build https://github.com/zefferno/bitcoin-tracker.git`
