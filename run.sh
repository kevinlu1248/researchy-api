cd /root/researchy-api
source venv/bin/activate
pip3 install -r requirements.txt
pkill gunicorn
screen -S api gunicorn --bind 0.0.0.0:80 app:app