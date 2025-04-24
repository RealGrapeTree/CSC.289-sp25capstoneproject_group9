FROM python:3.12.0

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install pytest 
COPY . .


EXPOSE 8000

CMD ["gunicorn", "app:app","--bind","0.0.0.0:8000"]