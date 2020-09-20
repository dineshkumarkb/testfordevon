FROM python:3.8
WORKDIR /myapp
COPY ./ ./
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["gunicorn","-w 4","-b", "0.0.0.0:5000","wsgi:app"]