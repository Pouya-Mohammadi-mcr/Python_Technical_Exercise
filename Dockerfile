FROM python:3

WORKDIR /Users/pouya/Python-Technical-Exercise

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY wsgi.ini .

CMD ["uwsgi", "wsgi.ini"]