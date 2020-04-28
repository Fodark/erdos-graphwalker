FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=app.py
CMD flask run -h 0.0.0.0 -p 5000