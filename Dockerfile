FROM python:3.8

WORKDIR /home
RUN apt-get update

RUN pip install --upgrade pip
RUN pip install django

EXPOSE 8080

ADD ./ ./sber

WORKDIR ./sber

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]