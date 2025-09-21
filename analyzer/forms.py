from django import forms
from .models import Contract

class ContractUploadForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'es. Contratto di Servizio - Cliente XYZ'
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.docx'
            })
        }
        
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise forms.ValidationError('Il file non può superare i 10MB')
            
            valid_extensions = ['.pdf', '.docx']
            if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
                raise forms.ValidationError('Sono supportati solo file PDF e DOCX')
        
        return file