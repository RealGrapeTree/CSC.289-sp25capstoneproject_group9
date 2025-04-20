FROM python:3.12.0-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py


EXPOSE 5000

CMD ["gunicorn", "app:app", "-b", "0.0.0.0:8000", "--workers=4"]