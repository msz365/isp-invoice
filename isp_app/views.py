from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy, reverse
from .models import *
from . import models
from django.views.generic import TemplateView,DetailView,ListView,View,CreateView,UpdateView, DeleteView
from . import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import render_to_pdf
from django.template.loader import get_template
from wkhtmltopdf.views import PDFTemplateView
import pdfkit
from isp_app.utils import render_to_pdf
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class CustomerListView(LoginRequiredMixin, ListView):
    model = models.Customer
    template_name='customerlist.html'
    queryset=Customer.objects.all().order_by('-id')
    context_object_name='customers'
    paginate_by=10
    def get_context_data(self,**kwargs):
        customers=Customer.objects.all().order_by('-id')
        search_term = ''
        context = super().get_context_data(**kwargs)
        if 'search' in self.request.GET:
            search_term = self.request.GET['search']
            customers=customers.filter(Q(customer_name__contains=search_term)|Q(customer_id__contains=search_term)|Q(contact_number__contains=search_term))
            context["qs"]=customers
        return context



class CustomerDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'customer'
    model = models.Customer
    template_name = 'customerdetails.html'
    def get_context_data(self,**kwargs):
        self.object = self.get_object()
        applicationform=self.object.applicationform
        invoiceotc=self.object.invoiceotc
        firstinvoice=self.object.firstinvoice
        context = super().get_context_data(**kwargs)
        context["invoice"]=invoiceotc
        context["firstinvoice"]=firstinvoice
        context["applicationform"]=applicationform
        return context




class ServiceListView(LoginRequiredMixin, ListView):
    model = models.Service
    template_name='servicelist.html'
    queryset=Service.objects.all()
    context_object_name='services'
    paginate_by=10
    def get_context_data(self,**kwargs):
        services=Service.objects.all()
        search_term = ''
        context = super().get_context_data(**kwargs)
        if 'search' in self.request.GET:
            search_term = self.request.GET['search']
            services=services.filter(Q(service_name__contains=search_term)|Q(service_type__contains=search_term))
            context["qs"]=services
            print(context)
        return context



class InvoiceListView(LoginRequiredMixin, ListView):
    model = models.Invoice
    template_name='invoicelist.html'
    queryset=Invoice.objects.all()
    context_object_name='invoices'
    paginate_by=10
    def get_context_data(self,**kwargs):
        invoices=Invoice.objects.all()
        search_term = ''
        context = super().get_context_data(**kwargs)
        if 'search' in self.request.GET:
            search_term = self.request.GET['search']
            invoices=invoices.filter(Q(invoice_number__contains=search_term))
            context["qs"]=invoices
        return context



class ServiceDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'service'
    model = models.Service
    template_name = 'servicedetails.html'



class InvoiceDetailView(LoginRequiredMixin, DetailView):
    context_object_name = 'invoice'
    model = models.Invoice
    template_name = 'invoicedetails.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        return context

class NewCustomerView(LoginRequiredMixin, CreateView):
    context_object_name = 'customer'
    form_class= forms.CustomerForm
    template_name = 'newcustomer.html'


class NewServiceView(LoginRequiredMixin, CreateView):
    context_object_name = 'service'
    form_class= forms.ServiceForm
    template_name = 'newservice.html'


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model=Customer
    context_object_name = 'customer'
    form_class= forms.CustomerForm
    template_name = 'customerupdate.html'


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model=Service
    context_object_name = 'service'
    form_class= forms.ServiceForm
    template_name = 'serviceupdate.html'

class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model=Customer
    context_object_name = 'customer'
    success_url=reverse_lazy('isp_app:customerlist')
    template_name='customerdeleteconfirm.html'


class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model=Service
    context_object_name = 'service'
    success_url=reverse_lazy('isp_app:servicelist')
    template_name='servicedeleteconfirm.html'



class NewInvoiceView(LoginRequiredMixin, CreateView):
    context_object_name = 'invoice'
    model=models.Invoice
    form_class= forms.InvoiceForm
    template_name = 'newinvoice.html'

class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model=Invoice
    context_object_name = 'invoice'
    form_class= forms.InvoiceForm
    template_name = 'invoiceupdate.html'

class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model=Invoice
    context_object_name = 'customer'
    success_url=reverse_lazy('isp_app:invoicelist')
    template_name='customerdeleteconfirm.html'

class InvoiceShowView(LoginRequiredMixin, DetailView):
    model = models.Invoice
    context_object_name = 'invoice'
    template_name = 'invoiceshow.html'

class InvoiceShowraView(LoginRequiredMixin, DetailView):
    model = models.Invoice
    context_object_name = 'invoice'
    template_name = 'invoiceshowra.html'


class GeneratePDF(DetailView):
    model = models.Invoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('invoiceshowpdf.html')
        context_object_name='invoice'
        context = super(GeneratePDF, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('invoiceshowpdf.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownload(DetailView):
    model = models.Invoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('invoiceshowpdf.html')
        context_object_name='invoice'
        context = super(GeneratePDFDownload, self).get_context_data(**kwargs)
        print(context)
        html = template.render(context)
        pdf = render_to_pdf('invoiceshowpdf.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class GeneratePDFra(DetailView):
    model = models.Invoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('invoiceshowpdfra.html')
        context_object_name='invoice'
        context = super(GeneratePDFra, self).get_context_data(**kwargs)
        print(context)
        html = template.render(context)
        print(html)
        pdf = render_to_pdf('invoiceshowpdfra.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownloadra(DetailView):
    model = models.Invoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('invoiceshowpdfra.html')
        context_object_name='invoice'
        context = super(GeneratePDFDownload, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('invoiceshowpdfra.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class GeneratePDFOTC(DetailView):
    model = models.InvoiceOTC
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('otc_ra.html')
        context_object_name='invoice'
        context = super(GeneratePDFOTC, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('otc_ra.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownloadOTC(DetailView):
    model = models.InvoiceOTC
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('otc_ra.html')
        context_object_name='invoiceotc'
        context = super(GeneratePDFDownloadOTC, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('otc_ra.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class GeneratePDFFirst(DetailView):
    model = models.FirstInvoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('firstinvoice.html')
        context_object_name='firstinvoice'
        context = super(GeneratePDFFirst, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('firstinvoice.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownloadFirst(DetailView):
    model = models.FirstInvoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('firstinvoice.html')
        context_object_name='firstinvoice'
        context = super(GeneratePDFDownloadFirst, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('firstinvoice.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")

class GeneratePDFFirstRA(DetailView):
    model = models.FirstInvoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('firstinvoicera.html')
        context_object_name='firstinvoice'
        context = super(GeneratePDFFirstRA, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('firstinvoicera.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownloadFirstRA(DetailView):
    model = models.FirstInvoice
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('firstinvoicera.html')
        context_object_name='firstinvoice'
        context = super(GeneratePDFDownloadFirstRA, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('firstinvoicera.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.invoice_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFApplicationForm(DetailView):
    model = models.ApplicationForm
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('applicationform.html')
        context_object_name='applicationform'
        context = super(GeneratePDFApplicationForm, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('applicationform.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.application_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownloadApplicationForm(DetailView):
    model = models.ApplicationForm
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('applicationform.html')
        context_object_name='applicationform'
        context = super(GeneratePDFDownloadApplicationForm, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('applicationform.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.application_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFApplicationFormRA(DetailView):
    model = models.ApplicationForm
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('applicationformra.html')
        context_object_name='applicationform'
        context = super(GeneratePDFApplicationFormRA, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('applicationformra.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.application_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "inline; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")


class GeneratePDFDownloadApplicationFormRA(DetailView):
    model = models.ApplicationForm
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        template = get_template('applicationformra.html')
        context_object_name='applicationform'
        context = super(GeneratePDFDownloadApplicationFormRA, self).get_context_data(**kwargs)
        html = template.render(context)
        pdf = render_to_pdf('applicationformra.html',context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = str(self.object.application_number+" "+self.object.customer.city+" "+self.object.customer.customer_name+".pdf")
            content = "attachment; filename=%s" %(filename)
            download = request.GET.get("download")
            if download:
                content = "attachment; filename=%s" %(filename)
            response['Content-Disposition'] = content
            return response
        return HttpResponse("Not found")
