from django.urls import path
from . import views


urlpatterns = [
    path('customer/', views.CustomerListView.as_view(),name='customerlist'),
    path('services/', views.ServiceListView.as_view(), name='servicelist'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoicelist'),
    path('customer/<pk>/', views.CustomerDetailView.as_view(), name='customerdetail'),
    path('services/<pk>/', views.ServiceDetailView.as_view(), name='servicedetail'),
    path('invoices/<pk>/', views.InvoiceDetailView.as_view(), name='invoicedetail'),
    path('newcustomer/', views.NewCustomerView.as_view(),name='newcustomer'),
    path('newservice/', views.NewServiceView.as_view(),name='newservice'),
    path('newinvoice/', views.NewInvoiceView.as_view(),name='newinvoice'),
    path('customerupdate/<pk>/', views.CustomerUpdateView.as_view(), name='customerupdate'),
    path('serviceupdate/<pk>/', views.ServiceUpdateView.as_view(), name='serviceupdate'),
    path('invoiceupdate/<pk>/', views.InvoiceUpdateView.as_view(), name='invoiceupdate'),
    path('customer/<pk>/delete', views.CustomerDeleteView.as_view(), name='customerdelete'),
    path('service/<pk>/delete', views.ServiceDeleteView.as_view(), name='servicedelete'),
    path('invoice/<pk>/delete', views.InvoiceDeleteView.as_view(), name='invoicedelete'),
    path('invoice/<pk>/show', views.InvoiceShowView.as_view(), name='invoiceshow'),
    path('invoices/<pk>/show', views.InvoiceShowraView.as_view(), name='invoiceshowra'),
    path('invoice/<pk>/pdf', views.GeneratePDF.as_view(), name='invoicepdf'),
    path('invoice/<pk>/pdf/download', views.GeneratePDFDownload.as_view(), name='invoicepdfdownload'),
    path('invoice/<pk>/pdfra', views.GeneratePDFra.as_view(), name='invoicepdfra'),
    path('invoice/<pk>/pdfra/download', views.GeneratePDFDownloadra.as_view(), name='invoicepdfdownloadra'),
    path('invoiceotc/<pk>/otc', views.GeneratePDFOTC.as_view(), name='customerotc'),
    path('invoiceotc/<pk>/otc/download', views.GeneratePDFDownloadOTC.as_view(), name='customerotcdownload'),
    path('firstinvoice/<pk>/first', views.GeneratePDFFirst.as_view(), name='firstinvoice'),
    path('firstinvoice/<pk>/first/download', views.GeneratePDFDownloadFirst.as_view(), name='firstinvoicedownload'),
    path('firstinvoicera/<pk>/first', views.GeneratePDFFirstRA.as_view(), name='firstinvoicera'),
    path('firstinvoicera/<pk>/first/download', views.GeneratePDFDownloadFirstRA.as_view(), name='firstinvoicedownloadra'),
    path('apllicationform/<pk>/', views.GeneratePDFApplicationForm.as_view(), name='applicationform'),
    path('apllicationform/<pk>/download', views.GeneratePDFDownloadApplicationForm.as_view(), name='applicationformdownload'),
    path('apllicationformra/<pk>/', views.GeneratePDFApplicationFormRA.as_view(), name='applicationformra'),
    path('apllicationformra/<pk>/download', views.GeneratePDFDownloadApplicationFormRA.as_view(), name='applicationformdownloadra'),

]
