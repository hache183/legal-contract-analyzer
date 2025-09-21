FROM python:3.11-slim

WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice
COPY . .

# Crea directory per media files
RUN mkdir -p media/contracts

# Espone la porta
EXPOSE 8000

# Comando di avvio
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]