from django.contrib import admin
from .models import Contract, RiskClause, Deadline

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['title', 'contract_type', 'risk_level', 'analyzed', 'uploaded_at']
    list_filter = ['contract_type', 'risk_level', 'analyzed', 'uploaded_at']
    search_fields = ['title', 'parties', 'ai_analysis']
    readonly_fields = ['uploaded_at', 'analysis_date', 'extracted_text']

@admin.register(RiskClause)
class RiskClauseAdmin(admin.ModelAdmin):
    list_display = ['contract', 'severity', 'risk_description']
    list_filter = ['severity', 'contract__contract_type']

@admin.register(Deadline)
class DeadlineAdmin(admin.ModelAdmin):
    list_display = ['contract', 'description', 'date']
    list_filter = ['date', 'contract__contract_type']