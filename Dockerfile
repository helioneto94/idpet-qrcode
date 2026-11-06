FROM python:3-alpine3.20
COPY ./src/requirements.txt .
RUN python -m pip install -r requirements.txt
WORKDIR /app
COPY ./src /app
EXPOSE 5000
ENTRYPOINT [ "python3", "app.py" ]