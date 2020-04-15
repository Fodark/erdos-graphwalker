#FROM gcr.io/distroless/python3-debian10
#COPY . /app
#WORKDIR /app
#RUN pip install -r requirements.txt
#ENTRYPOINT ["python"]
#CMD ["app.py"]

FROM python:3.8-slim AS build-env
ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

FROM gcr.io/distroless/python3-debian10
COPY --from=build-env /app /app
COPY --from=build-env /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
WORKDIR /app
ENV PYTHONPATH=/usr/local/lib/python3.8/site-packages
EXPOSE 5000
CMD ["app.py"]