FROM python:3.10

COPY requirements.txt .

RUN pip install -r requirements.txt

# CMD ["python", "./sample_data_parsing.py"]

CMD tail -f /dev/null
