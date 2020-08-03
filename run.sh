source venv/bin/activate
pip3 install -r /root/researchy-api/requirements.txt
pkill gunicorn
gunicorn --bind 0.0.0.0:80 app:app