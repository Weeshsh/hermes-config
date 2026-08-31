FROM nousresearch/hermes-agent

USER root
RUN apt-get update && apt-get install -y \
    nano \
    python3 \
    python3-pip \
    python3-venv \
    python3-caldav \
    curl \
    git \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN curl -OL https://go.dev/dl/go1.22.5.linux-amd64.tar.gz && \
    tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz && \
    rm go1.22.5.linux-amd64.tar.gz

RUN /opt/hermes/.venv/bin/python -m ensurepip && /opt/hermes/.venv/bin/python -m pip install --no-cache-dir caldav


ENV PATH="/usr/local/go/bin:${PATH}"
ENV GOPATH="/root/go"
ENV PATH="${GOPATH}/bin:${PATH}"

WORKDIR /opt/data

CMD ["gateway", "run"]
