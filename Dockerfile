FROM python:3.9

EXPOSE 10000

WORKDIR /service

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT ["uvicorn", "main:app", "--port", "10000", "--host", "0.0.0.0"]

#uvicorn main:app --port 10000 --host 0.0.0.0