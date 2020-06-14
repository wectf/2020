FROM python:3.8.2-alpine3.11

WORKDIR /home/src
COPY . .
RUN pip install pyjwt
CMD ["python3", "server.py"]