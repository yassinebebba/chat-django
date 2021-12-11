FROM python

WORKDIR /opt/chat_django

ENV PORT 8000
ENV VIRTUAL_ENV=/opt/chat_django/venv

RUN python -m venv $VIRTUAL_ENV

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt /opt/chat_django/

COPY twilio.env /opt/chat_django/

CMD [".", "twilio.env"]

RUN pip install -r requirements.txt

COPY . /opt/chat_django

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "chat.asgi", "-w", "4", "-k" , "uvicorn.workers.UvicornWorker"]
