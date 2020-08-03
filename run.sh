source venv/bin/activate
pip3 install -r requirements.txt
pkill gunicorn3
gunicorn3 --bind 0.0.0.0:5000 app:app