FROM python:3.9
WORKDIR /app
COPY . /app
RUN apt-get update && apt-get install -y netcat
RUN pip install -r requirements.txt
ENTRYPOINT ["/app/entrypoint.sh"]