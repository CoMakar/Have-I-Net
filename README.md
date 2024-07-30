# Have I-Net

<img src="examples/preview.png" style="border-radius: 32px"> 

**Have I-Net** is a terminal-based application that allows
you to monitor the ping latency of multiple servers in real-time.
This tool helps in tracking the network performance and
detecting potential connectivity issues.


## Features
* Monitor multiple servers simultaneously
* Real-time ping latency updates
* Easy-to-read terminal interface
* Configurable refresh interval


## Keys
* A - Add new host
* C - Toggle compact mode
* Q \ E - Decrease \ Increase ping interval


## How to Run \ Build from source
```shell
# enter the shell
$ pipenv shell

# RUN
# ----------------------------
# install dependencies
$ pipenv install

# run
$ python main.py
# ----------------------------

# BUILD
# ----------------------------
# install dev dependencies
$ pipenv install --dev

# build
$ pyinstaller main.spec
# or
$ make build
# ----------------------------
```
