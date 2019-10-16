FROM python:3.7

ADD ./app /app
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip
RUN pip install -Ur /tmp/requirements.txt
WORKDIR /app

EXPOSE 80
ENV MESSAGE "Go ahead, make my day..."
CMD ["python", "app.py"]