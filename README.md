/usr/local/bin/netwatch.py

sudo nano /etc/systemd/system/netwatch.service
ini
[Unit]
Description=Network Monitor & Recovery
After=network-online.target

[Service]
ExecStart=/usr/bin/python3 /usr/local/bin/netwatch.py
Restart=always
User=root

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable --now netwatch.service


/var/tmp/net_fail_count.txt — счётчик ошибок

/var/tmp/last_reboot.txt — отметка времени последней перезагрузки