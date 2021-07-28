from django.contrib import admin
from isp_app.models import Service,Customer, Invoice,Tax, InvoiceOTC, FirstInvoice, ApplicationForm
from import_export.admin import ImportExportModelAdmin
from import_export import resources



class CustomerResource(resources.ModelResource):

    class Meta:
        model = Customer

class CustomerAdmin(ImportExportModelAdmin):
    resource_class=CustomerResource



class ServiceResource(resources.ModelResource):

    class Meta:
        model = Service

class ServiceAdmin(ImportExportModelAdmin):
    resource_class=ServiceResource

class InvoiceResource(resources.ModelResource):

    class Meta:
        model = Invoice

class InvoiceAdmin(ImportExportModelAdmin):
    resource_class=InvoiceResource

class TaxResource(resources.ModelResource):

    class Meta:
        model = Tax

class TaxAdmin(ImportExportModelAdmin):
    resource_class=TaxResource


class InvoiceOTCResource(resources.ModelResource):

    class Meta:
        model = InvoiceOTC

class InvoiceOTCAdmin(ImportExportModelAdmin):
    resource_class=InvoiceOTCResource

class FirstInvoiceResource(resources.ModelResource):

    class Meta:
        model = FirstInvoice

class FirstInvoiceAdmin(ImportExportModelAdmin):
    resource_class=FirstInvoiceResource


class ApplicationFormResource(resources.ModelResource):

    class Meta:
        model = ApplicationForm

class ApplicationFormAdmin(ImportExportModelAdmin):
    resource_class=ApplicationFormResource

admin.site.register(Service, ServiceAdmin)
admin.site.register(Customer,CustomerAdmin)
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Tax,TaxAdmin)
admin.site.register(InvoiceOTC,InvoiceOTCAdmin)
admin.site.register(FirstInvoice,FirstInvoiceAdmin)
admin.site.register(ApplicationForm,ApplicationFormAdmin)
