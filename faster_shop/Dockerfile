FROM python:3.8.2-alpine3.11
RUN apk add --no-cache sqlite-dev

WORKDIR /home/src
RUN pip install flask peewee gunicorn
COPY . .
CMD ["gunicorn", "app:app", "--workers", "20", "--timeout", "2", "-b", "0.0.0.0:1002"]
