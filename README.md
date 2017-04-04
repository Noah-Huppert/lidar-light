# Lidar Lite
This repository holds the code necessary to use a Garmin Lidar Lite V3 unit with an Omega. Code is written in Python 2. 
Version 3 should be supported however the Omega runs Python 2.

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
