# Installation

```
sudo apt install python3-pygame pigpio
```

Enable `pgiod.service`

```
sudo systemctl enable --now pigpiod.service 
```

## System Service

Create the file `/etc/systemd/system/hut.service' with the following content:

```
[Unit]
Description=Hut service
[Service]
User=pi
Group=pi
Type=simple
ExecStart=/usr/bin/python3 /home/pi/hut_niklas/main.py
[Install]
WantedBy=multi-user.target
```

and enable it
```
sudo systemctl enable --now hut.service
```
