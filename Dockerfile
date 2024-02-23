FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . . 

ENV DISPLAY=host.docker.internal:0.0

CMD ["python", "main.py"]
