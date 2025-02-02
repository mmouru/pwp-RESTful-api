FROM python:3.8.10-slim-buster

ENV DOCKER True
ENV FLASK_APP dogdict

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

WORKDIR /src/app/

COPY . .

# Creates initial test db
RUN flask init-db

CMD ["flask", "run", "--host=0.0.0.0"]
