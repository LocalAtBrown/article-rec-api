# if this python version changes, the python version in pyproject.toml needs to change too
FROM python:3.9
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "/app/app.py"]
