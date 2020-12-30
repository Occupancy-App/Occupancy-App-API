FROM python:3.9-alpine 

# Client connections -- 8000 is client connections, 9000 is Prometheus metrics
EXPOSE 8000 9000

COPY requirements.txt /tmp

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Ensures stdout and stderr are not buffered, that ensures that output
#       hits Docker logs ASAP
ENV PYTHONUNBUFFERED=1 

# Don't bother writing PYC to disk -- that's only if you run the code twice, and containers
#   get no benefit
ENV PYTHONDONTWRITEBYTECODE=1

# Create a user account to run the code from, that's fine as we're on a non-privileged port
RUN adduser --disabled-password apiuser
WORKDIR /home/apiuser/api_app
USER apiuser

# Do the copy of source AFTER installing dependencies, that way we don't have to build 
#   dependencies every time, we can use that cached Docker image layer
COPY src/ ./

ENTRYPOINT [ "python", "occupancy_api_endpoint.py" ]
