from django.db import models
from django.db.models import DateTimeField, ExpressionWrapper, F, DateField,Sum,Count
from django.db import models
from django.urls import reverse_lazy, reverse
from datetime import date,datetime
import inflect,string
import datetime
from django.utils.translation import gettext as _
import re
from django.contrib import auth
from accounts.models import User
from django.conf import settings
from django.db.models.signals import pre_save, post_save




class AnnotationManager(models.Manager):

    def __init__(self, **kwargs):
        super().__init__()
        self.annotations = kwargs

    def get_queryset(self):
        return super().get_queryset().annotate(**self.annotations)



class Tax(models.Model):
    TAX_TYPE=(
    ('Simple', 'Simple'),
    ('Compound', 'Compound')
    )
    tax_name=models.CharField(max_length=100)
    tax_percentage=models.DecimalField(max_digits=5, decimal_places=3)
    tax_type=models.CharField(max_length=100, choices=TAX_TYPE, default=None)

    def __str__(self):
        return self.tax_name



class Service(models.Model):
    SERVICE_TYPE = (
            ('CIR', 'CIR'),
            ('Shared','Shared'),
            ('Business Plus','Business Plus'),
            ('L2 Data','L2 Data'),
            ('VPS','VPS'),
            ('Hosted Server','Hosted Server'),
            ('Live IP','Live IP'),
            ('Rental','Rental'),
        )
    service_name = models.CharField(max_length=200)
    service_type = models.CharField(max_length=100, choices=SERVICE_TYPE, default=None)
    service_qunatity = models.FloatField()
    service_unit_price = models.FloatField()
    service_tax=models.ManyToManyField(Tax, blank=True)
    #_total=None
    #objects = AnnotationManager(total=(F('service_qunatity')*F('service_unit_price')))


    def __str__(self):
        return str(self.service_name)

    def get_tax(self):
        queryset=self.service_tax.all()
        return queryset


    def total_billing(self):
        return self.service_tax.aggregate(total_tax=models.Sum((F('service_qunatity')*F('service_unit_price'))))['total']

    def cost_pretax(self):
        return self.service_qunatity*self.service_unit_price

    def get_gst(self):
        temp_total=self.service_qunatity*self.service_unit_price
        temp_total_tax=0
        if self.service_tax.all().exists():
            for tax in self.service_tax.all().filter(tax_type__contains='Simple'):
                temp_total_tax=temp_total*tax.tax_percentage
            return int(temp_total_tax)
        else:
            return 0

    def get_wht(self):
        temp_total=self.service_qunatity*self.service_unit_price
        temp_total_tax=0
        if self.service_tax.all().exists():
            for tax in self.service_tax.all().filter(tax_type__contains='Simple'):
                temp_total_tax= temp_total_tax+(temp_total*tax.tax_percentage)
            temp_total=temp_total+temp_total_tax
            temp_total_tax=0
            for tax in self.service_tax.all().filter(tax_type__contains='Compound'):
                temp_total_tax=temp_total_tax+(temp_total*tax.tax_percentage)
            return int(temp_total_tax)
        else:
            return 0

    def total_service_cost(self):
        temp_total=self.service_qunatity*self.service_unit_price
        temp_total_tax=0
        if self.service_tax.all().exists():
            for tax in self.service_tax.all().filter(tax_type__contains='Simple'):
                temp_total_tax= temp_total_tax+(temp_total*float(tax.tax_percentage))
            temp_total=temp_total+temp_total_tax
            for tax in self.service_tax.all().filter(tax_type__contains='Compound'):
                temp_total=temp_total+(temp_total*float(tax.tax_percentage))
            return int(temp_total)
        else:
            temp_total=self.service_qunatity*self.service_unit_price
            return int(temp_total)

    def get_absolute_url(self):
        return reverse("isp_app:servicedetail", args=[str(self.id)])


    def get_service_per_day(self):
            total=0
            per_day=0
            total=self.cost_pretax()
            per_day=int(total/30)
            return per_day

    def service_cost_first(self, days):
        total=(self.get_service_per_day())*days
        return total

class Customer(models.Model):
    STATUS_LIST=(
            ('Active','Active'),
            ('Inactive','Inactive'),
            ('Disconnected','Disconnected')
    )
    BILLING_COMPANY= (
            ('SKIF','SKIF'),
            ('RA','RA')
    )
    TAXPAYER_STATUS =  (
            ('Individual','Individual'),
            ('Company','Company'),
        )
    customer_name = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, blank=True)
    address = models.CharField(max_length=350)
    billing_address = models.CharField(max_length=350)
    city = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=200)
    colocation = models.CharField(max_length=150)
    ntn_cnic = models.CharField(max_length=200)
    taxpayer_status = models.CharField(max_length=100, choices=TAXPAYER_STATUS, default=None)
    taxpayer_name = models.CharField(max_length=200)
    connection_date = models.DateField()
    billing_company = models.CharField(max_length=100, choices=BILLING_COMPANY, default=None)
    cnic_pic = models.ImageField(upload_to="gallery", default=None)
    service_subscribed = models.ManyToManyField(Service)
    total_billing = models.IntegerField()
    otc=models.IntegerField()
    status = models.CharField(max_length=100, choices=STATUS_LIST, default='Active')
    ipaddr = models.CharField(max_length=200)


    def __str__(self):
        return str(self.customer_name)

    def get_company(self):
        company=self.billing_company
        skif="SKIF"
        ra="RA"
        if company==skif:
            return 1
        else:
            return 0

    def get_gst(self):
        total_gst=0
        for service in self.service_subscribed.all():
            temp_total=service.service_qunatity*service.service_unit_price
            temp_total_tax=0
            if service.service_tax.all().exists():
                for tax in service.service_tax.all().filter(tax_type__contains='Simple'):
                    temp_total_tax=temp_total*tax.tax_percentage
                    total_gst+=temp_total_tax
            else:
                total_gst=0
        return int(total_gst)

    def get_wht(self):
        total_wht=0
        total_gst=0
        for service in self.service_subscribed.all():
            temp_total=service.service_qunatity*service.service_unit_price
            temp_total_tax=0
            if service.service_tax.all().exists():
                for tax in service.service_tax.all().filter(tax_type__contains='Simple'):
                    temp_total_tax=(service.service_qunatity*service.service_unit_price)*tax.tax_percentage
                    temp_total+=temp_total_tax
                for tax in service.service_tax.all().filter(tax_type__contains='Compound'):
                    total_wht=total_wht+(temp_total*tax.tax_percentage)
            else:
                total=0
        return int(total_wht)


    def total_service_cost(self):
        total=0
        total_gst=self.get_gst()
        total_wht=self.get_wht()
        base_amount= self.total_billing()
        total=base_amount+total_wht+total_gst
        return int(total)

    def total_service_cost_ra(self):
        total=0
        base_amount= self.total_billing()
        total=base_amount
        return int(total)

    def get_services(self):
        return self.service_subscribed

    def get_words(self):
        total = self.total_service_cost()
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)

    def get_words_otc(self):
        total = self.otc
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)

    def amount_after_due_date(self):
        base_amount= self.total_service_cost()
        overdue=base_amount+(base_amount*0.1)
        return overdue
    def amount_after_due_date_ra(self):
        base_amount= self.total_service_cost_ra()
        overdue=base_amount+(base_amount*0.1)
        return overdue

    def total_billing(self):
        return self.service_subscribed.aggregate(total=models.Sum((F('service_qunatity')*F('service_unit_price'))))['total']

    def total_billing1(self):
        self.total_billing=self.service_subscribed.aggregate(total=models.Sum((F('service_qunatity')*F('service_unit_price'))))['total']
        return self.total_billing

    def get_absolute_url(self):
        return reverse("isp_app:customerdetail", args=[str(self.id)])

    def get_companywise_count(self):
        qs= Customer.objects.all().filter(status='Active')
        skif=qs.filter(billing_company='SKIF').count()
        return skif

    def get_companywise_countra(self):
        qs= Customer.objects.all().filter(status='Active')
        ra=qs.filter(billing_company='RA').count()
        return ra

    def get_skif_revenue(self):
        qs= Customer.objects.all().filter(status='Active')
        skif=qs.filter(billing_company='SKIF')
        total_revenue=0
        for customer in skif:
            total_revenue+=customer.total_billing()
        return int(total_revenue)

    def get_ra_revenue(self):
        qs= Customer.objects.all().filter(status='Active')
        ra=qs.filter(billing_company='RA')
        total_revenue=0
        for customer in ra:
            total_revenue+=customer.total_billing()
        return int(total_revenue)

    def get_city_wise_customer_count_skif(self):
        qs= Customer.objects.all().filter(status='Active')
        skif=qs.filter(billing_company='SKIF')
        return str(list(skif.values('city').order_by().annotate(Count('city')).values_list('city__count', flat=True)))[1:-1]

    def get_city_wise_customer_count_ra(self):
        qs= Customer.objects.all().filter(status='Active')
        ra=qs.filter(billing_company='RA')
        return int(str(list(ra.values('city').order_by().annotate(Count('city')).values_list('city__count', flat=True)))[1:-1])

    def get_cities(self):
        qs= Customer.objects.all().filter(status='Active')
        ra=qs.filter(billing_company='RA')
        cities=Customer.objects.values('city').distinct()
        return str(list(cities.values_list('city', flat=True)))[1:-1]


    def save(self, *args, **kwargs):
        is_first=True
        for customer in Customer.objects.all():
            if customer.id==self.id:
                super().save(*args, **kwargs)
                is_first=False
        if is_first:
            super().save(*args, **kwargs)
            app_form=ApplicationForm(customer=self)
            app_form.save()
            temp=InvoiceOTC(customer=self)
            temp.save()
            temp2=FirstInvoice(customer=self)
            temp2.save()


    def increment_customer_id():
        last_id = Customer.objects.filter(billing_company='SKIF').order_by('id').last()
        #print(Invoice.objects.filter(customer__billing_company='SKIF'))
        if not last_id:
             return 'ISP100001'
        invoice_no = last_id.customer_id
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'ISP' + str(new_invoice_int)
        return new_invoice_no

    def increment_customer_idra():
        last_id = Customer.objects.filter(billing_company='RA').order_by('id').last()
        #print (Invoice.objects.filter(customer__billing_company='RA'))
        if not last_id:
             return 'ISPR100001'
        invoice_no = last_id.customer_id
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'ISPR' + str(new_invoice_int)
        return new_invoice_no

    customer_id=models.CharField(max_length=500, default=increment_customer_id, null=True, blank=True )

def customer_pre_save_receiver(sender, instance, *args, **kwargs):
    is_first=True
    for customer in Customer.objects.all():
        if customer.id == instance.id:
            is_first=False
    if is_first:
        if instance.billing_company=="SKIF":
            instance.customer_id=Customer.increment_customer_id()
        else:
            instance.customer_id=Customer.increment_customer_idra()

pre_save.connect(customer_pre_save_receiver, sender=Customer)


class Invoice(models.Model):

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created=models.DateField(auto_now=False,auto_now_add=True)
    date_updated=models.DateField(auto_now=True,auto_now_add=False)
    invoice_created_by=models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null=True, on_delete=models.CASCADE, editable=False)
    invoice_date=models.DateField(_("Invoice Date"), default=datetime.date.today)

    @property
    def customeraddress(self):
        return self.customer.address


    def __str__(self):
        return self.invoice_number

    def get_month(self):
        inv_date=int(self.invoice_date.strftime("%m"))
        if inv_date==1:
            return "January"
        elif inv_date==2:
            return "February"
        elif inv_date==3:
            return "March"
        elif inv_date==4:
            return "April"
        elif inv_date==5:
            return "May"
        elif inv_date==6:
            return "June"
        elif inv_date==7:
            return "July"
        elif inv_date==8:
            return "August"
        elif inv_date==9:
            return "September"
        elif inv_date==10:
            return "October"
        elif inv_date==11:
            return "November"
        elif inv_date==12:
            return "December"


    def get_duedate(self):
        return self.invoice_date + datetime.timedelta(7)

    def get_absolute_url(self):
        return reverse("isp_app:invoicedetail", args=[str(self.id)])

    def increment_invoice_number():
        last_invoice = Invoice.objects.filter(customer__billing_company='SKIF').order_by('id').last()
        #print(Invoice.objects.filter(customer__billing_company='SKIF'))
        if not last_invoice:
             return 'ISP1359'
        invoice_no = last_invoice.invoice_number
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'ISP' + str(new_invoice_int)
        return new_invoice_no

    def increment_invoice_numberra():
        last_invoice = Invoice.objects.filter(customer__billing_company='RA').order_by('id').last()
        #print (Invoice.objects.filter(customer__billing_company='RA'))
        if not last_invoice:
             return 'ISPR100'
        invoice_no = last_invoice.invoice_number
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'ISPR' + str(new_invoice_int)
        return new_invoice_no

    invoice_number=models.CharField(max_length=500, default=increment_invoice_number, null=True, blank=True )

    def get_company(self):
        company=self.customer.billing_company
        skif="SKIF"
        ra="RA"
        if company==skif:
            return 1
        else:
            return 0




def invoice_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.customer.billing_company=="SKIF":
        instance.invoice_number=Invoice.increment_invoice_number()
    else:
        instance.invoice_number=Invoice.increment_invoice_numberra()

pre_save.connect(invoice_pre_save_receiver, sender=Invoice)

class InvoiceOTC(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    date_created=models.DateField(auto_now=False,auto_now_add=True)
    date_updated=models.DateField(auto_now=True,auto_now_add=False)
    invoice_created_by=models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null=True, on_delete=models.CASCADE, editable=False)
    invoice_date=models.DateField(auto_now=False,auto_now_add=True)

    @property
    def customeraddress(self):
        return self.customer.address


    def __str__(self):
        return self.invoice_number


    def get_invoice_day(self):
        return int(self.invoice_date.strftime("%d"))


    def get_month(self):
        inv_date=int(self.invoice_date.strftime("%m"))
        if inv_date==1:
            return "January"
        elif inv_date==2:
            return "February"
        elif inv_date==3:
            return "March"
        elif inv_date==4:
            return "April"
        elif inv_date==5:
            return "May"
        elif inv_date==6:
            return "June"
        elif inv_date==7:
            return "July"
        elif inv_date==8:
            return "August"
        elif inv_date==9:
            return "September"
        elif inv_date==10:
            return "October"
        elif inv_date==11:
            return "November"
        elif inv_date==12:
            return "December"


    def get_duedate(self):
        return self.invoice_date

    def get_absolute_url(self):
        return reverse("isp_app:invoicedetail", args=[str(self.id)])

    def increment_invoice_number():
        last_invoice = InvoiceOTC.objects.filter(customer__billing_company='SKIF').order_by('id').last()
        #print(Invoice.objects.filter(customer__billing_company='SKIF'))
        if not last_invoice:
             return 'OTC1359'
        invoice_no = last_invoice.invoice_number
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'OTC' + str(new_invoice_int)
        return new_invoice_no

    def increment_invoice_numberra():
        last_invoice = InvoiceOTC.objects.filter(customer__billing_company='RA').order_by('id').last()
        #print (Invoice.objects.filter(customer__billing_company='RA'))
        if not last_invoice:
             return 'OTCR100'
        invoice_no = last_invoice.invoice_number
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'OTCR' + str(new_invoice_int)
        return new_invoice_no

    invoice_number=models.CharField(max_length=500, default=increment_invoice_number, null=True, blank=True )

    def get_company(self):
        company=self.customer.billing_company
        skif="SKIF"
        ra="RA"
        if company==skif:
            return 1
        else:
            return 0


    def get_remaing_days_in_month(self):
        current=int(self.invoice_date.strftime("%d"))
        if int(self.invoice_date.strftime("%m"))==9 or int(self.invoice_date.strftime("%m"))==4 or int(self.invoice_date.strftime("%m"))==6 or int(self.invoice_date.strftime("%m"))==11:
            remaining=30-current
        elif int(self.invoice_date.strftime("%m"))==2:
            remaining=28-current
        else:
            remaining=31-current
        return int(remaining)


    def get_invoice_total(self):
        total=0
        total+=int(self.customer.otc)
        return int(total)

    def get_words_total(self):
        total = self.get_invoice_total()
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)




def invoiceotc_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.customer.billing_company=="SKIF":
        instance.invoice_number=InvoiceOTC.increment_invoice_number()
    else:
        instance.invoice_number=InvoiceOTC.increment_invoice_numberra()

pre_save.connect(invoiceotc_pre_save_receiver, sender=InvoiceOTC)



# def customer_pre_save_receiver(sender, instance, *args, **kwargs):
#         qs=Customer.objects.all()
#         is_present=False
#         for customer in qs:
#             if instance.id==customer.id:
#                 is_present=True
#
#         if is_present:
#             print("updated")
#         else:
#             print("new")




# pre_save.connect(customer_pre_save_receiver, sender=Customer)


class FirstInvoice(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    date_created=models.DateField(auto_now=False,auto_now_add=True)
    date_updated=models.DateField(auto_now=True,auto_now_add=False)
    invoice_created_by=models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null=True, on_delete=models.CASCADE, editable=False)
    invoice_date=models.DateField(auto_now=False,auto_now_add=True)

    @property
    def customeraddress(self):
        return self.customer.address


    def __str__(self):
        return self.invoice_number


    def get_invoice_day(self):
        return int(self.invoice_date.strftime("%d"))


    def get_month(self):
        inv_date=int(self.invoice_date.strftime("%m"))
        if inv_date==1:
            return "January"
        elif inv_date==2:
            return "February"
        elif inv_date==3:
            return "March"
        elif inv_date==4:
            return "April"
        elif inv_date==5:
            return "May"
        elif inv_date==6:
            return "June"
        elif inv_date==7:
            return "July"
        elif inv_date==8:
            return "August"
        elif inv_date==9:
            return "September"
        elif inv_date==10:
            return "October"
        elif inv_date==11:
            return "November"
        elif inv_date==12:
            return "December"


    def get_duedate(self):
        return self.invoice_date

    def get_absolute_url(self):
        return reverse("isp_app:invoicedetail", args=[str(self.id)])

    def increment_invoice_number():
        last_invoice = InvoiceOTC.objects.filter(customer__billing_company='SKIF').order_by('id').last()
        #print(Invoice.objects.filter(customer__billing_company='SKIF'))
        if not last_invoice:
             return 'FIS1359'
        invoice_no = last_invoice.invoice_number
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'FIS' + str(new_invoice_int)
        return new_invoice_no

    def increment_invoice_numberra():
        last_invoice = InvoiceOTC.objects.filter(customer__billing_company='RA').order_by('id').last()
        #print (Invoice.objects.filter(customer__billing_company='RA'))
        if not last_invoice:
             return 'FIRA100'
        invoice_no = last_invoice.invoice_number
        invoice_int = int(re.split('(\d+)',invoice_no)[1])
        new_invoice_int = invoice_int + 1
        new_invoice_no = 'FIRA' + str(new_invoice_int)
        return new_invoice_no

    invoice_number=models.CharField(max_length=500, default=increment_invoice_number, null=True, blank=True )

    def get_company(self):
        company=self.customer.billing_company
        skif="SKIF"
        ra="RA"
        if company==skif:
            return 1
        else:
            return 0


    def get_remaing_days_in_month(self):
        current=int(self.invoice_date.strftime("%d"))
        if int(self.invoice_date.strftime("%m"))==9 or int(self.invoice_date.strftime("%m"))==4 or int(self.invoice_date.strftime("%m"))==6 or int(self.invoice_date.strftime("%m"))==11:
            remaining=30-current
        elif int(self.invoice_date.strftime("%m"))==2:
            remaining=28-current
        else:
            remaining=31-current
        return int(remaining)


    def get_invoice_total(self):
        total=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
        return int(total)

    def get_words_total(self):
        total = self.get_invoice_total()
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)

    def get_invoice_total_skif(self):
        total=0
        total_gst=0
        total_wht=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
            total_gst+=total*0.195
        for service in self.customer.service_subscribed.all():
            if service.service_type=='L2 Data':
                total_wht+=0
            else:
                total_wht+=((service.get_service_per_day()*days)+((service.get_service_per_day()*days)*0.195))*0.125
        grand_total=total+total_gst+total_wht
        return int(grand_total)


    def after_due(self):
        within_due=self.get_invoice_total_skif()
        aafter_due=within_due+(within_due*0.1)
        return int(aafter_due)


    def get_gst_skif(self):
        total=0
        total_gst=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
            total_gst+=total*0.195
        return int(total_gst)

    def get_wht_skif(self):
        total=0
        total_gst=0
        total_wht=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
            total_gst+=total*0.195
        for service in self.customer.service_subscribed.all():
            if service.service_type=='L2 Data':
                total_wht+=0
            else:
                total_wht+=((service.get_service_per_day()*days)+((service.get_service_per_day()*days)*0.195))*0.125
        return int(total_wht)

    def get_words_total_skif(self):
        total = self.get_invoice_total_skif()
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)



def first_invoice_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.customer.billing_company=="SKIF":
        instance.invoice_number=FirstInvoice.increment_invoice_number()
    else:
        instance.invoice_number=FirstInvoice.increment_invoice_numberra()

pre_save.connect(first_invoice_pre_save_receiver, sender=FirstInvoice)




class ApplicationForm(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    date_created=models.DateField(auto_now=False,auto_now_add=True)
    date_updated=models.DateField(auto_now=True,auto_now_add=False)
    application_created_by=models.ForeignKey(settings.AUTH_USER_MODEL, default=1, null=True, on_delete=models.CASCADE, editable=False)
    application_date=models.DateField(auto_now=False,auto_now_add=True)

    @property
    def customeraddress(self):
        return self.customer.address


    def __str__(self):
        return self.application_number


    def get_application_day(self):
        return int(self.application_date.strftime("%d"))


    def get_month(self):
        inv_date=int(self.application_date.strftime("%m"))
        if inv_date==1:
            return "January"
        elif inv_date==2:
            return "February"
        elif inv_date==3:
            return "March"
        elif inv_date==4:
            return "April"
        elif inv_date==5:
            return "May"
        elif inv_date==6:
            return "June"
        elif inv_date==7:
            return "July"
        elif inv_date==8:
            return "August"
        elif inv_date==9:
            return "September"
        elif inv_date==10:
            return "October"
        elif inv_date==11:
            return "November"
        elif inv_date==12:
            return "December"


    def get_duedate(self):
        return self.application_date

    def get_absolute_url(self):
        return reverse("isp_app:applicationdetail", args=[str(self.id)])

    def increment_application_number():
        last_application = ApplicationForm.objects.filter(customer__billing_company='SKIF').order_by('id').last()
        #print(application.objects.filter(customer__billing_company='SKIF'))
        if not last_application:
             return 'NAS1000'
        application_no = last_application.application_number
        application_int = int(re.split('(\d+)',application_no)[1])
        new_application_int = application_int + 1
        new_application_no = 'NAS' + str(new_application_int)
        return new_application_no

    def increment_application_numberra():
        last_application = ApplicationForm.objects.filter(customer__billing_company='RA').order_by('id').last()
        #print (application.objects.filter(customer__billing_company='RA'))
        if not last_application:
             return 'NARA1000'
        application_no = last_application.application_number
        application_int = int(re.split('(\d+)',application_no)[1])
        new_application_int = application_int + 1
        new_application_no = 'NARA' + str(new_application_int)
        return new_application_no

    application_number=models.CharField(max_length=500, default=increment_application_number, null=True, blank=True )

    def get_company(self):
        company=self.customer.billing_company
        skif="SKIF"
        ra="RA"
        if company==skif:
            return 1
        else:
            return 0


    def get_remaing_days_in_month(self):
        current=int(self.application_date.strftime("%d"))
        if int(self.application_date.strftime("%m"))==9 or int(self.application_date.strftime("%m"))==4 or int(self.application_date.strftime("%m"))==6 or int(self.application_date.strftime("%m"))==11:
            remaining=30-current
        elif int(self.application_date.strftime("%m"))==2:
            remaining=28-current
        else:
            remaining=31-current
        return int(remaining)


    def get_application_total(self):
        total=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
        return int(total)

    def get_words_total(self):
        total = self.get_application_total()
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)

    def get_application_total_skif(self):
        total=0
        total_gst=0
        total_wht=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
            total_gst+=total*0.195
        for service in self.customer.service_subscribed.all():
            if service.service_type=='L2 Data':
                total_wht+=0
            else:
                total_wht+=((service.get_service_per_day()*days)+((service.get_service_per_day()*days)*0.195))*0.125
        grand_total=total+total_gst+total_wht
        return int(grand_total)


    def after_due(self):
        within_due=self.get_application_total_skif()
        aafter_due=within_due+(within_due*0.1)
        return int(aafter_due)


    def get_gst_skif(self):
        total=0
        total_gst=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
            total_gst+=total*0.195
        return int(total_gst)

    def get_wht_skif(self):
        total=0
        total_gst=0
        total_wht=0
        days=self.get_remaing_days_in_month()
        for service in self.customer.service_subscribed.all():
            total+=(service.get_service_per_day()*days)
            total_gst+=total*0.195
        for service in self.customer.service_subscribed.all():
            if service.service_type=='L2 Data':
                total_wht+=0
            else:
                total_wht+=((service.get_service_per_day()*days)+((service.get_service_per_day()*days)*0.195))*0.125
        return int(total_wht)

    def get_words_total_skif(self):
        total = self.get_application_total_skif()
        p = inflect.engine()
        text=p.number_to_words(total)
        return string.capwords(text)



def application_form_pre_save_receiver(sender, instance, *args, **kwargs):
    # is_first=True
    # for customer in Customer.objects.all():
    #     if customer.id == instance.customer.id:
    #         is_first=False
    # if is_first:
        if instance.customer.billing_company=="SKIF":
            instance.application_number=ApplicationForm.increment_application_number()
        else:
            instance.application_number=ApplicationForm.increment_application_numberra()


pre_save.connect(application_form_pre_save_receiver, sender=ApplicationForm)
