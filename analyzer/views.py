import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Contract, RiskClause, Deadline
from .forms import ContractUploadForm
from .utils import extract_text_from_file, clean_text
from .services import ContractAIService

logger = logging.getLogger(__name__)

def home(request):
    """Homepage con statistiche rapide"""
    total_contracts = Contract.objects.count()
    analyzed_contracts = Contract.objects.filter(analyzed=True).count()
    high_risk_contracts = Contract.objects.filter(risk_level__in=['high', 'critical']).count()
    
    recent_contracts = Contract.objects.order_by('-uploaded_at')[:5]
    
    context = {
        'total_contracts': total_contracts,
        'analyzed_contracts': analyzed_contracts,
        'high_risk_contracts': high_risk_contracts,
        'recent_contracts': recent_contracts,
    }
    
    return render(request, 'analyzer/home.html', context)

def upload_contract(request):
    """Upload e analisi automatica del contratto"""
    if request.method == 'POST':
        form = ContractUploadForm(request.POST, request.FILES)
        if form.is_valid():
            contract = form.save()
            
            try:
                # Estrazione del testo
                file_path = contract.file.path
                extracted_text = extract_text_from_file(file_path)
                cleaned_text = clean_text(extracted_text)
                
                contract.extracted_text = cleaned_text
                contract.save()
                
                # Avvia analisi AI in background (in produzione usare Celery)
                analyze_contract_ai(contract.id)
                
                messages.success(request, f'Contratto "{contract.title}" caricato con successo! Analisi in corso...')
                return redirect('contract_detail', pk=contract.pk)
                
            except Exception as e:
                logger.error(f"Errore nell'elaborazione del contratto {contract.id}: {str(e)}")
                messages.error(request, f'Errore nell\'elaborazione del file: {str(e)}')
                return redirect('upload_contract')
    else:
        form = ContractUploadForm()
    
    return render(request, 'analyzer/upload.html', {'form': form})

def analyze_contract_ai(contract_id):
    """Analizza il contratto con AI"""
    try:
        contract = Contract.objects.get(id=contract_id)
        
        if not contract.extracted_text:
            raise Exception("Testo non disponibile per l'analisi")
        
        # Analisi AI
        ai_response = ContractAIService.analyze_contract(contract.extracted_text)
        
        # Salva sempre la risposta grezza per debug
        contract.ai_analysis = ai_response
        
        try:
            # Rimuovi eventuali markdown wrapper
            cleaned_response = ai_response.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response.replace('```json', '').replace('```', '').strip()
            
            # Parsing della risposta JSON
            ai_data = json.loads(cleaned_response)
            
            # Aggiorna il contratto con i risultati
            contract.contract_type = ContractAIService.extract_contract_type(contract.extracted_text)
            contract.parties = ai_data.get('parties', '')
            contract.duration = ai_data.get('duration', '')
            contract.key_obligations = ai_data.get('key_obligations', '')
            
            # Salva clausole rischiose
            risk_clauses_data = ai_data.get('risk_clauses', [])
            for clause_data in risk_clauses_data:
                RiskClause.objects.create(
                    contract=contract,
                    clause_text=clause_data.get('clause', ''),
                    risk_description=clause_data.get('risk', ''),
                    severity=clause_data.get('severity', 'low'),
                    recommendation=clause_data.get('recommendation', '')
                )
            
            # Salva scadenze
            deadlines_data = ai_data.get('deadlines', [])
            for deadline_data in deadlines_data:
                Deadline.objects.create(
                    contract=contract,
                    description=deadline_data.get('description', ''),
                )
            
            # Calcola livello di rischio in base alle clausole trovate
            high_risk_count = sum(1 for clause in risk_clauses_data if clause.get('severity') in ['high', 'critical'])
            if high_risk_count >= 3:
                contract.risk_level = 'critical'
            elif high_risk_count >= 2:
                contract.risk_level = 'high'
            elif high_risk_count >= 1:
                contract.risk_level = 'medium'
            else:
                contract.risk_level = 'low'
            
        except json.JSONDecodeError as e:
            print(f"Errore JSON parsing: {e}")
            print(f"Risposta AI: {ai_response[:500]}...")
            # Se la risposta non è JSON valido, usa valori di default
            contract.risk_level = 'medium'
            contract.contract_type = ContractAIService.extract_contract_type(contract.extracted_text)
        
        contract.analyzed = True
        contract.analysis_date = timezone.now()
        contract.save()
        
    except Exception as e:
        logger.error(f"Errore nell'analisi AI del contratto {contract_id}: {str(e)}")
        try:
            contract = Contract.objects.get(id=contract_id)
            contract.ai_analysis = f"Errore nell'analisi automatica: {str(e)}"
            contract.analyzed = True
            contract.analysis_date = timezone.now()
            contract.risk_level = 'medium'
            contract.contract_type = 'other'
            contract.save()
        except Contract.DoesNotExist:
            logger.error(f"Contratto {contract_id} non trovato durante gestione errore")

class ContractListView(ListView):
    model = Contract
    template_name = 'analyzer/contract_list.html'
    context_object_name = 'contracts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Contract.objects.all()
        
        # Filtri
        contract_type = self.request.GET.get('type')
        risk_level = self.request.GET.get('risk')
        
        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['contract_types'] = Contract.CONTRACT_TYPES
        context['risk_levels'] = Contract.RISK_LEVELS
        return context

class ContractDetailView(DetailView):
    model = Contract
    template_name = 'analyzer/contract_detail.html'
    context_object_name = 'contract'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['risk_clauses'] = self.object.risk_clauses.all()
        context['deadlines'] = self.object.deadlines.all()
        return context

@csrf_exempt
def reanalyze_contract(request, pk):
    """Rianalizza un contratto esistente"""
    if request.method == 'POST':
        contract = get_object_or_404(Contract, pk=pk)
        
        # Cancella analisi precedente
        contract.risk_clauses.all().delete()
        contract.deadlines.all().delete()
        
        # Reset dei campi di analisi
        contract.analyzed = False
        contract.analysis_date = None
        contract.ai_analysis = ''
        contract.parties = ''
        contract.duration = ''
        contract.key_obligations = ''
        contract.risk_level = ''
        contract.save()
        
        # Rianalizza
        analyze_contract_ai(contract.id)
        
        return JsonResponse({'status': 'success', 'message': 'Rianalisi completata'})
    
    return JsonResponse({'status': 'error', 'message': 'Metodo non consentito'})