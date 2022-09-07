FROM python:3
ENV PYTHONUNBUFFERED 1 

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
ENV EMAIL_HOST 'smtp.gmail.com'
ENV EMAIL_PORT '587'
ENV JWT_SECRET_KEY "JWT_SECRET_KEY1234567890"
## Missing Email Host user and password

CMD sh -c "python manage.py makemigrations && \
                    python manage.py migrate && \
                    python manage.py runserver 0.0.0.0:8000"
