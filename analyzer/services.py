import openai
import re
from datetime import datetime, timedelta
from django.conf import settings
from decouple import config

openai.api_key = config('OPENAI_API_KEY')

class ContractAIService:
    
    @staticmethod
    def analyze_contract(text):
        """Analisi completa del contratto con AI"""
        
        prompt = f"""
        Analizza questo contratto legale in italiano con la competenza di un avvocato specializzato in diritto civile e commerciale.
        
        TESTO DEL CONTRATTO:
        {text[:4000]}  # Limitiamo per evitare token limit
        
        Fornisci un'analisi strutturata in formato JSON con le seguenti chiavi:
        
        {{
            "contract_type": "tipo di contratto identificato",
            "parties": "descrizione delle parti coinvolte",
            "duration": "durata del contratto e scadenze principali",
            "key_obligations": "obblighi principali per ciascuna parte",
            "risk_level": "low/medium/high/critical",
            "risk_clauses": [
                {{
                    "clause": "testo della clausola problematica",
                    "risk": "descrizione del rischio legale",
                    "severity": "low/medium/high/critical",
                    "recommendation": "raccomandazione legale specifica"
                }}
            ],
            "deadlines": [
                {{
                    "description": "descrizione della scadenza",
                    "timeframe": "periodo di tempo o data"
                }}
            ],
            "summary": "riassunto esecutivo dell'analisi legale"
        }}
        
        Focus su:
        - Clausole penali eccessive
        - Squilibri contrattuali
        - Rischi di inadempimento
        - Clausole vessatorie
        - Termini di recesso
        - Responsabilità e garanzie
        - Compliance GDPR (se applicabile)
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Sei un avvocato esperto in diritto civile e commerciale italiano. Analizza i contratti con precisione tecnica e linguaggio professionale ma accessibile."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Errore nell'analisi AI: {str(e)}"
    
    @staticmethod
    def extract_contract_type(text):
        """Identifica il tipo di contratto"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['compravendita', 'vendita', 'acquisto']):
            return 'purchase'
        elif any(word in text_lower for word in ['prestazione', 'servizio', 'consulenza']):
            return 'service'
        elif any(word in text_lower for word in ['lavoro', 'dipendente', 'assunzione']):
            return 'employment'
        elif any(word in text_lower for word in ['locazione', 'affitto', 'noleggio']):
            return 'rental'
        elif any(word in text_lower for word in ['riservatezza', 'confidenzialità', 'nda']):
            return 'nda'
        elif any(word in text_lower for word in ['partnership', 'collaborazione', 'joint']):
            return 'partnership'
        elif any(word in text_lower for word in ['licenza', 'concessione', 'diritti']):
            return 'license'
        else:
            return 'other'
    
    @staticmethod
    def calculate_risk_level(risk_clauses):
        """Calcola il livello di rischio complessivo"""
        if not risk_clauses:
            return 'low'
        
        high_risk_count = sum(1 for clause in risk_clauses if clause.get('severity') in ['high', 'critical'])
        
        if high_risk_count >= 3:
            return 'critical'
        elif high_risk_count >= 2:
            return 'high'
        elif high_risk_count >= 1:
            return 'medium'
        else:
            return 'low'