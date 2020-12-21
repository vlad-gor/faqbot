cp faqbot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable faqbot
systemctl start faqbot
systemctl status faqbot