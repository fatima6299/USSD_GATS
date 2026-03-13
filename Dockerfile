FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data

COPY . .

RUN if [ -f commandes.db ]; then mv commandes.db /app/data/; fi
RUN if [ -f repas.db ]; then mv repas.db /app/data/; fi

RUN adduser -D ussduser
RUN chown -R ussduser:ussduser /app
USER ussduser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]