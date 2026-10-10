from django import forms
from d_analysis.models import Upload

class ExcelUploadForm(forms.ModelForm):
    """This form securely accepts and validates uploaded Excel workbooks"""
    
    class Meta:
        model = Upload
        fields = ['file']
        widgets = {
            'file' : forms.ClearableFileInput(attrs={
                'class' : 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-violet-50 file:text-violet-700 hover:file:bg-violet-100 cursor-pointer',
                'accept' : '.xlsx'
            })
        }
    
    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            if not uploaded_file.name.lower().endswith('.xlsx'):
                raise forms.ValidationError("Only Excel workbooks (.xlsx) are allowed.")
            if uploaded_file.size > 15 * 1024 *1024: # 15MB Limit
                raise forms.ValidationError("File size exceeds the 15MB limit.")
        return uploaded_file