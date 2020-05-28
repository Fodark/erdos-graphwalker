FROM joyzoursky/python-chromedriver:3.8-selenium
WORKDIR /var/app
ADD . /var/app
RUN pip install --no-cache-dir -r requirements.txt
RUN printf "search 192.168.1.144\nnameserver 8.8.8.8\noptions ndots:0" > /etc/resolv.conf 
CMD python ltc.py