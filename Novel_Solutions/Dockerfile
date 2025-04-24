FROM python:3.12.0-slim

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt
RUN pip install pytest 
COPY . .

ENV FLASK_APP=app.py


EXPOSE 5000

CMD ["flask", "run" , "--host=0.0.0.0", "--port=5000"]