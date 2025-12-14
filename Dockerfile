FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

RUN DATABASE_URL="" python manage.py collectstatic --noinput

# Compile translation messages
RUN DATABASE_URL="" python manage.py compilemessages --ignore=venv 2>/dev/null || true

EXPOSE 8000

CMD ["./entrypoint.sh"]
