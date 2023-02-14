# Use an official Python image as the base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Switch to bash as the default shell
SHELL ["/bin/bash", "-c"]

# Create a virtual environment and install required packages
RUN pip install virtualenv
RUN virtualenv env
RUN source env/bin/activate
RUN pip install django
RUN apt-get update && apt-get install -y python3-opencv
RUN pip install opencv-python

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install packages from the requirements.txt file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code, including the createsuperuser.py script, to the container
COPY . .

# Set the environment variables
# ENV DJANGO_SETTINGS_MODULE=pos.settings

# Copy the createsuperuser.py script into the /app directory
COPY createsuperuser.py /app/

# Expose the port 8000
EXPOSE 8000

# Command to run when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]