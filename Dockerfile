FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DISPLAY=host.docker.internal:0.0

# Build cmd: docker build . -t image_name

# Run cmd: docker run -it --rm --name my-running-app image_name
CMD ["python", "./main.py"]
