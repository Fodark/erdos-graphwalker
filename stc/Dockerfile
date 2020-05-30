FROM python:3.8-alpine as build-env
COPY . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

FROM python:3.8-alpine
COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.8/site-packages
CMD "./wait-for" "neo:7474" "--" "python" "stc.py"
