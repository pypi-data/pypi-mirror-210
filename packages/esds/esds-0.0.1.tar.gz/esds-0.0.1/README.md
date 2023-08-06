
# ESDS: An Extensible Simulator For Distributed Systems and Cyber-Physical Systems
[![Dependency](https://img.shields.io/badge/Python-v3.10-blue)](https://www.python.org/) [![Pipeline](https://gitlab.com/manzerbredes/esds/badges/main/pipeline.svg)](https://gitlab.com/manzerbredes/esds/-/tree/main)

### What is ESDS ?
It is a short learning curve and coarse-grain network simulator. It contains the essential building blocks for the simulation of *Distributed Systems*, *Cyber-Physical Systems* (CPS), *Wireless Sensors Networks* (WSN) scenarios. It was originally designed to improve the flexibility/faithfulness of nodes implementations and mitigate the learning curve compare to existing network simulators. 

ESDS is part of a research project. Studies and validation experiments are available online. For more details please visit http://todo.com.

### Installation
`> pip install esds`

To ensure that esds is properly working and installed on your system, you can run the simulation tests with one of the following scripts:
- `tests/run.sh`
- `tests/run.py`

### Features
- Easy to use
- Small API
- Agent-based: node implementations are located in independant python files
- Wireless interferences detection (i.e no modelization)
- Custom node mobility (by updating the network matrix)
- Nodes plugins (e.g energy consumption)

### What ESDS does not implements ?
- Network protocols (e.g IP/TCP/UDP)
- Wireless physical layer models (e.g Friis and Log-Distance models, modulation, RSSI)
- Routing algorithms (e.g Shortest path)
- And much more!

### Simulation API
- `api.args`
- `api.send(<int>,<data>,<size>,<dst>)`
- `api.sendt(<int>,<data>,<size>,<dst>,<t>)`
- `api.receive(<int>)`
- `api.receivet(<int>,<t>)`
- `api.wait(<t>)`
- `api.wait_end()`
- `api.log(<message>)`
- `api.read(<register>)`
- `api.turn_on()`
- `api.turn_off()`
- *More details on the API in [example/sender.py](example/sender.py)*

### Documentation
See `manual/manual.pdf` and the source code in `example/` and`tests/`. 
