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

# Crea directory per media e static files
RUN mkdir -p media/contracts static

# Colleziona file statici
RUN python manage.py collectstatic --noinput --settings=contract_analyzer.settings

# Espone la porta
EXPOSE 8000

# Comando di avvio
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "contract_analyzer.wsgi:application"]