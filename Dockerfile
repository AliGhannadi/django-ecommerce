FROM python:3.13

WORKDIR /app/core

# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 

# RUN pip config set global.index-url https://mirror2.chabokan.net/pypi/simple/
# RUN pip install --upgrade pip -i https://mirror2.chabokan.net/pypi/simple/


COPY requirements.txt .

RUN pip install --no-cache-dir \
    -r requirements.txt 

COPY . .

# Expose the Django port
EXPOSE 8000

# Run Django’s development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
