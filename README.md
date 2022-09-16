# ARProof (tuxcut fork)
A front-end Cli-app utility for Tuxcut's daemon. This program will protect your linux PC from ARP spoofing attack.

Since the tuxcut GUI (Official client) was broken and seems to be abandoned, I decided to write my own client for the tuxcut's daemon server.
This method is proven to be effective againts NetCut atleast in my case. Executing this program will also spoof your PC's MAC address. 

Note : This program is for linux distributions with Systemd only! \
Tested on Mint 21

## Requirements

You must have : 
  - python >= 3.5 
  - Zenity ( Used for dialog pop-up )

## Installation Guide
1. Clone this repository

```bash
git clone https://github.com/2k16daniel/ARProof.git
```

2. Install the required dependencies

```bash
cd ARProof && python -m pip install -r requirements.txt
```

3. Build and install the package

```bash
python setup.py install
```

## Usage

For your convinience, you must run this daemon under Systemd but you can also run this via terminal
1. Start the daemon, run

```bash
 sudo tuxcutd
```

2. To enable protection + MAC spoof, run
```bash
arproof
```
The arproof will not run in background, the daemon will do the work \
Note : The daemon must run in background thats why it would be better if you make a systemd service/UNIT file.

## Sample Systemd service file
You can copy my service file if you want :)
```service
[Unit]
Description=TuxCut server
After=network.target

[Service]
User=root
Group=root
ExecStart=tuxcutd

[Install]
WantedBy=multi-user.target

```

