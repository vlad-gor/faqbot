systemctl stop faqbot
systemctl status faqbot
sudo pip3 install spacy
sudo python3 -m spacy download de_core_news_sm
sudo python3 -m spacy download en_core_web_sm
systemctl start faqbot
systemctl status faqbot