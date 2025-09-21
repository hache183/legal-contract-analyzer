🏛️ Legal Contract Analyzer - README
Panoramica
Legal Contract Analyzer è un'applicazione Django che combina intelligenza artificiale e competenze legali specialistiche per l'analisi automatica di contratti. Sviluppato con background in Giurisprudenza + Tecnologia, offre analisi professionali per identificare rischi, clausole problematiche e obblighi contrattuali.
Caratteristiche Principali

Analisi AI Avanzata: Utilizzo di GPT-3.5 per analisi semantica dei contratti
Identificazione Rischi: Rilevamento automatico di clausole potenzialmente problematiche
Estrazione Intelligente: Parsing automatico di PDF e DOCX
Dashboard Professionale: Interface user-friendly con Bootstrap 5
Containerizzazione: Deploy ready con Docker
Background Legal-Tech: Sviluppato con competenze in Digital Law e GDPR

Stack Tecnologico

Backend: Django 4.2, Python 3.11
AI Integration: OpenAI GPT-3.5 Turbo
Document Processing: python-docx, PyPDF2
Frontend: Bootstrap 5, Font Awesome
Database: SQLite (dev), PostgreSQL ready
Containerization: Docker & Docker Compose

Quick Start
bash# Clone repository
git clone https://github.com/your-username/legal-contract-analyzer.git
cd legal-contract-analyzer

# Setup ambiente virtuale
python -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Configura variabili ambiente
cp .env.example .env
# Modifica .env con la tua OPENAI_API_KEY

# Setup database
python manage.py migrate
python manage.py createsuperuser

# Avvia server
python manage.py runserver
Deploy con Docker
bashdocker-compose up --build
Competenze Legal-Tech
Questo progetto dimostra l'integrazione di:

Diritto Civile e Commerciale: Analisi contratti secondo normativa italiana
Digital Law: Competenze in contratti digitali e e-commerce
GDPR Compliance: Verifica clausole privacy e trattamento dati
AI Integration: Utilizzo professionale di Large Language Models
Web Development: Full-stack Django con best practices