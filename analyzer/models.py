import os
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class Contract(models.Model):
    CONTRACT_TYPES = [
        ('purchase', 'Contratto di Compravendita'),
        ('service', 'Contratto di Servizio'),
        ('employment', 'Contratto di Lavoro'),
        ('rental', 'Contratto di Locazione'),
        ('nda', 'Accordo di Riservatezza'),
        ('partnership', 'Contratto di Partnership'),
        ('license', 'Contratto di Licenza'),
        ('other', 'Altro'),
    ]
    
    RISK_LEVELS = [
        ('low', 'Basso'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Critico'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Titolo Contratto")
    file = models.FileField(
        upload_to='contracts/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        verbose_name="File Contratto"
    )
    uploaded_at = models.DateTimeField(default=timezone.now)
    
    # Risultati analisi AI
    contract_type = models.CharField(
        max_length=20, 
        choices=CONTRACT_TYPES, 
        blank=True,
        verbose_name="Tipo Contratto"
    )
    parties = models.TextField(blank=True, verbose_name="Parti Coinvolte")
    duration = models.CharField(max_length=500, blank=True, verbose_name="Durata")
    key_obligations = models.TextField(blank=True, verbose_name="Obblighi Principali")
    risk_level = models.CharField(
        max_length=10, 
        choices=RISK_LEVELS, 
        blank=True,
        verbose_name="Livello di Rischio"
    )
    extracted_text = models.TextField(blank=True)
    ai_analysis = models.TextField(blank=True, verbose_name="Analisi AI")
    
    # Metadata
    analyzed = models.BooleanField(default=False)
    analysis_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Contratto"
        verbose_name_plural = "Contratti"
    
    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)


class RiskClause(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Basso'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Critico'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='risk_clauses')
    clause_text = models.TextField(verbose_name="Testo della Clausola")
    risk_description = models.TextField(verbose_name="Descrizione del Rischio")
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, verbose_name="Gravità")
    recommendation = models.TextField(verbose_name="Raccomandazione")
    
    class Meta:
        verbose_name = "Clausola Rischiosa"
        verbose_name_plural = "Clausole Rischiose"


class Deadline(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='deadlines')
    description = models.CharField(max_length=500, verbose_name="Descrizione Scadenza")
    date = models.DateField(null=True, blank=True, verbose_name="Data Scadenza")
    days_notice = models.IntegerField(null=True, blank=True, verbose_name="Giorni di Preavviso")
    
    class Meta:
        ordering = ['date']
        verbose_name = "Scadenza"
        verbose_name_plural = "Scadenze"