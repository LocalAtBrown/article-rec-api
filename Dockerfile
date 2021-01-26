FROM python:3.9
WORKDIR /app
COPY setup.py .
COPY lib/__init__.py lib/__init__.py
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . .
CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "app:app"]
