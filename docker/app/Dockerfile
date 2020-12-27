FROM python:3.9-alpine 

WORKDIR /usr/src/app

EXPOSE 80

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Do the copy of source AFTER installing dependencies, that way we don't have to build 
#   dependencies every time, we can use that cached Docker image layer
COPY src/ ./

ENTRYPOINT [ "python", "-u", "occupancy_api_endpoint.py" ]
