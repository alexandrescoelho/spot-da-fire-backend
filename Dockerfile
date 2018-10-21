FROM python:3.6
MAINTAINER XenonStack

# Creating Application Source Code Directory
RUN mkdir -p /spot-da-fire-backend/

# Setting Home Directory for containers
WORKDIR /spot-da-fire-backend/

# Installing python dependencies
COPY requirements.txt /spot-da-fire-backend/
COPY credentials.json /spot-da-fire-backend/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#RUN pip install disaster-checklist-backend/external_libs/disaster_checklist-0.1/

# Copying src code to Container
COPY . /spot-da-fire-backend/app

# Application Environment variables
ENV APP_ENV development

# Exposing Ports
EXPOSE 5000

# Setting Persistent data
VOLUME ["/app-data"]

# Running Python Application
CMD ["python", "./app/app.py"]
#CMD ["python", "-m", "flask", "run"]
