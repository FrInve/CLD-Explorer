FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    libcairo2 \
    python3-pydot graphviz \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/
RUN pip3 install -r requirements.txt

ADD ./ /app/

EXPOSE 8501

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s CMD curl --fail localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "Causal_Loops_Explorer.py", "--server.port=8501", "--server.address=0.0.0.0"]
