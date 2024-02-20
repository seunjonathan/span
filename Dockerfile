# Before doing a PUSH to Azure registry, login with this: az acr login --name <name goes here>
# Read this for details on deploying to Azure: https://docs.microsoft.com/en-ca/azure/python/tutorial-deploy-containers-02

# If docker registry in Azure is seaspan.azurecr.io, so name of a docker image should be
# something like seaspan.azurecr.io/<name-of-webapp>:latest

# If you need to use Flask (instead of something based on ASGI) and you need to have the best performance possible,
# you can use the alternative image: tiangolo/meinheld-gunicorn-flask.
FROM tiangolo/uwsgi-nginx-flask:python3.9
LABEL Name=python-rest-webapp Version=0.1.0

# Set the port on which the app runs; make both values the same.
#
# IMPORTANT: When deploying to Azure App Service, go to the App Service on the Azure 
# portal, navigate to the Applications Settings blade, and create a setting named
# WEBSITES_PORT with a value that matches the port here (the Azure default is 80).
# You can also create a setting through the App Service Extension in VS Code.
ENV LISTEN_PORT=5000
EXPOSE 5000

# Indicate where uwsgi.ini lives
ENV UWSGI_INI uwsgi.ini

# Tell nginx where static files live. Typically, developers place static files for
# multiple apps in a shared folder, but for the purposes here we can use the one
# app's folder. Note that when multiple apps share a folder, you should create subfolders
# with the same name as the app underneath "static" so there aren't any collisions
# when all those static files are collected together.
ENV STATIC_URL /rest_app/static

# On linux kimage will attempt to create a .cache dir here:
# '$HOME/.cache/scikit-image'
ENV HOME /rest_app
RUN echo $HOME

# Set the folder where uwsgi looks for the app
WORKDIR /rest_app

# Copy the app contents to the image
COPY . /rest_app

# If you have additional requirements beyond Flask (which is included in the
# base image), generate a requirements.txt file with pip freeze and uncomment
# the next three lines.
COPY requirements.txt /
RUN pip install --no-cache-dir -U pip
RUN pip install --no-cache-dir -r /requirements.txt

# This was my original line
# RUN python3 -m pip install -r requirements.txt

# apt-get install dependent binaries here 
RUN apt-get -y update

# We are getting this error when the image runs: PermissionError: [Errno 13] Permission denied: '/rest_app/.cache/scikit-image'
# I believe that skimage is creating a cache folder in an area where the default 
#   docker user does not have permission.
# The fix according to https://code.visualstudio.com/docs/containers/python-user-rights is:
# (probably the mkdir is what made it work)
# RUN useradd appuser && chown -R appuser /rest_app
# RUN mkdir /rest_app/.cache/scikit-image
# RUN chown -R appuser /rest_app/.cache/scikit-image
