FROM python:3.12.0-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .


EXPOSE 8000

CMD ["gunicorn", "app:app","0.0.0.0:8000"]