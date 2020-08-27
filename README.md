## TuxCut 
A utility that protect linux computers againest arpspoof attacks

## Features:
- Hide your machine (ip/MAC) from arp scanner utilities.
- list all the live host in your LAN.
- cut the connection between any live host and the gateway.
- use wondershaper to control your upload or download speed limits.

## Screenshot
#### 6.1
![selection_001](https://user-images.githubusercontent.com/536140/30778321-344ce456-a0d3-11e7-81c3-e7bcbd28a88d.png)

## Install
Get your package from [Download](https://github.com/a-atalla/tuxcut/releases) section

# Run from source
- create virtualenv `python3 -m venv env_name`.
- activate the environment `source env_name/bin/activate`.
- Get [WxPython](https://extras.wxpython.org/wxPython4/extras/linux/gtk3/) and install it inside the active venv `pip install wxPython-4.xxxxx.whl`
- install the rest of python packages `pip install -r requirements.txt`.
- run the server with root priviliages `sudo env_name/bin/python3 server/tuxcutd.py`.
- run the gui `env_name/bin/python3 client/tuxcut.py`.
- To build packages you need to install [FPM](https://github.com/jordansissel/fpm)  then run the script `build.sh`
