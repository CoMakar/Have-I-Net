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
# ~ RUN ~

# enter the shell
$ pipenv shell

# install dependencies
$ pipenv install

# run
$ python main.py

# ~ BUILD ~

# ! WARNING !
# - Due to a pyinstaller bug related to the Windows Terminal
#   At the moment dev build of the pyinstaller is used
#   So you need to set an environment variable to compile the
#   Pyinstaller bootloader

# enter the shell
$ pipenv shell

# set pyinstaller environment variable
# for powershell
$ $Env:PYINSTALLER_COMPILE_BOOTLOADER = 1
# |
# for CMD
$ set PYINSTALLER_COMPILE_BOOTLOADER=1

# install dev dependencies
$ pipenv install --dev

# build
# using pyinstaller
$ pyinstaller main.spec
# |
# using make
$ make build

```
