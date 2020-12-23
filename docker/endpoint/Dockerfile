FROM python:3-alpine AS dependencies

WORKDIR /usr/src/app

EXPOSE 443

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy latest certificate files
COPY ./certs/fullchain.pem ./tls_cert/
COPY ./certs/privkey.pem   ./tls_cert/

# Do the copy of source AFTER installing dependencies, that way we don't have to build 
#   dependencies every time, we can use that cached Docker image layer
COPY src/ ./

ENTRYPOINT [ "python", "occupancy_api_endpoint.py" ]
