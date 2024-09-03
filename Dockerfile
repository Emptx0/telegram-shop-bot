FROM python:3.12

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt
CMD python3 src/installer.py --nointeract && python3 src/main.py