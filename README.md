# Lidar Omega (py)
This repository holds code necessary to use use a Lidar Lite v3 unit with an Omega. Programmed in Python 2.

# Table Of Contents
- [Overview](#overview)
- [Setup](#setup)
- [Lidar Lite Class](#lidar-lite-class)
- [Web Server](#web-server)

# Overview
This repository provides 2 components. A `LidarLite` class for use in interfacing with a Lidar Lite v3 unit. And a simple webserver which serves a page with a distance and velocity graph:

![Webpage distance and velocity graph screenshot](https://github.com/Noah-Huppert/lidar-lite/raw/master/screenshot.png).

# Setup
This project uses GNU Make, SSH, SSH Pass, and SCP to manage and run code on the Omega. Please ensure these programs are 
installed before using.

This project also assumes you are connected to your Omega's wifi hotspot and it can be reached at `192.168.3.1`. If the 
host is different pass the `DEVICE_HOST` variable to Make during use (Like so: `make DEVICE_HOST=192.168.1.1`).

Finally this project assumes that there is a file named `password` in the root of this directory which contains the 
Omega's password. This is automatically gitignored.

## Omega Setup
To install Python 2 and all required dependencies on the Omega run the `python-setup` Make target.

# Running On Omega
The `Makefile` provides several helpful targets. In most cases you can just run `make` and the latest code will be uploaded 
and run on the Omega. 

## all
This target will run the `main.py` and `index.html` targets.

## index.html
This target will upload all files in the `static` directory to the Omega.

## main.py
This target will upload the `main.py` file to the Omega and run it.

# Lidar Lite Class
The `LidarLite` class provides a Python wrapper around the Lidar Lite v3 hardware. It provides several helper functions. As well as an API around the registers in the device.

See the [`main.py` file](https://github.com/Noah-Huppert/lidar-lite/blob/7d72758e611fb4f451706f99cdd54669cd158f47/main.py#L577) for a list of register key names. The API wrapper around the registers on the device is provided by [py-i2c-register](https://github.com/Noah-Huppert/py-i2c-register). You may access a Py I2C Register`RegisterList` class in the `controls` field of a `LidarLite` class instance. This allows you to read and or write to and from all registers provided by the device.

# Web Server
When run the `main.py` file will launch a Flask web server. This will serve an `index.html` page which will show a graph of the distance and velocity measurements read off your device in real time.  

This is done by contacting an API also hosted by the same Flask web server. This API has 2 endpoints: `/distance` and `/velocity`.  These both trigger a read on the Lidar Lite device, and return the coresponding values.

This web server is run on the Omega itself. So it can only be accessed if you are connected to the device's wifi.
