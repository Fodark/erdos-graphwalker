FROM joyzoursky/python-chromedriver:3.8-alpine3.10-selenium
WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD "./wait-for" "neo:7474" "--" "python" "ltc.py"