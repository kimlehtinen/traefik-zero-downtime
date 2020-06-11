FROM python:2.7

RUN apt-get update
RUN apt-get install -y git

RUN  apt-get -yq update && \
     apt-get -yqq install ssh

# RUN git clone https://github.com/kim3z/flask-docker-app.git

COPY . /app
WORKDIR /app

# WORKDIR /flask-docker-app

RUN pip install -r requirements.txt

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app.py"]