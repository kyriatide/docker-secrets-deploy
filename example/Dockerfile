FROM debian:bullseye-slim

RUN apt-get -qq update && \
    # required dependencies if not available already
    apt-get -qq -y install git python3-minimal

COPY ./config/ /config/

RUN git clone https://github.com/kyriatide/docker-secrets-deploy.git

ENTRYPOINT ["python3", "/docker-secrets-deploy/run.py"]

# use the cmd directive for your command and arguments to be run at startup
CMD ["cat", "/config/example.conf"]
