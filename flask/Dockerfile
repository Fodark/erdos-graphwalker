FROM tiangolo/uwsgi-nginx-flask:python3.6-alpine3.8
RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=app.py
CMD ./wait-for neo:7474 -- flask run -h 0.0.0.0 -p 5000