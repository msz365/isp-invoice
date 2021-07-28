from django import forms
from .models import Customer,Invoice,Service,Tax

from datetime import date,datetime
import datetime




class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields='__all__'



class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields='__all__'

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields='__all__'

        widgets = {
        'invoice_date': forms.DateInput(format=('%d/%m/%Y'), attrs={'class':'datepicker', 'placeholder':'Invoice Date', 'type':'date' }),
    }
