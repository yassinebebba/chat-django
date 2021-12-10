FROM python:3

ENV PORT 8000
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /chat_django

COPY requirements.txt /chat_django/
COPY twilio.env /chat_django/

CMD [".", "twilio.env"]

CMD ["python", "-m", "venv", "venv"]

CMD [".", "venv/bin/activate"]

RUN pip install -r requirements.txt

COPY . /chat_django

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "chat.asgi", "-w", "4", "-k" , "uvicorn.workers.UvicornWorker"]
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]