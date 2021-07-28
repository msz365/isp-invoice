from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from isp_app.models import Customer,Invoice,Service
from django.db.models import Count
import re


class HomePage(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)

        #City List
        cities_list=[]
        cities1=Customer.objects.all().filter(status='Active').values('city').distinct().reverse()
        abc=cities1.values_list('city', flat=True)
        for item in abc:
            cities_list.append(item)
        qs= Customer.objects.all().filter(status='Active')

        #SKIF customer Count City Wise
        skif_count_per_city=[]
        city_total=0
        for city in cities_list:
            for customer in Customer.objects.all().filter(status='Active').filter(billing_company='SKIF'):
                if customer.city==city:
                    city_total+=1
            skif_count_per_city.append(city_total)
            city_total=0


        #RA customer Count City Wise
        ra_count_per_city=[]
        city_total=0
        for city in cities_list:
            for customer in Customer.objects.all().filter(status='Active').filter(billing_company='RA'):
                if customer.city==city:
                    city_total+=1
            ra_count_per_city.append(city_total)
            city_total=0


        #SKIF Revenue per City
        skif_revenue_per_city=[]
        city_total=0
        for city in cities_list:
            for customer in Customer.objects.all().filter(status='Active').filter(billing_company='SKIF'):
                if customer.city==city:
                    city_total+=customer.total_billing1()
            skif_revenue_per_city.append(city_total)
            city_total=0


        #RA Revenue per City
        ra_revenue_per_city=[]
        city_total=0
        for city in cities_list:
            for customer in Customer.objects.all().filter(status='Active').filter(billing_company='RA'):
                if customer.city==city:
                    city_total+=customer.total_billing1()
            ra_revenue_per_city.append(city_total)
            city_total=0



        #Services List
        services_offered=Service.objects.all().values('service_type').distinct().reverse()
        temp1=services_offered.values_list('service_type', flat=True)
        services=[]
        for item in temp1:
            services.append(item)

        #Services SKIF Count
        skif_service_count=[]
        service_total=0
        for service in services:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(service_subscribed__service_type__startswith=service).count()
            skif_service_count.append(temp2)




        #Services RA Count
        ra_service_count=[]
        service_total=0
        for service in services:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(service_subscribed__service_type__startswith=service).count()
            ra_service_count.append(temp2)


        #CIR Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="CIR").count()
            list1.append(temp2)
        str1=map(str,list1)
        cir_skif=list(str1)
        #CIR Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="CIR").count()
            list1.append(temp2)
        str1=map(str,list1)
        cir_ra=list(str1)

        #Live IP Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="Live IP").count()
            list1.append(temp2)
        str1=map(str,list1)
        ip_skif=list(str1)
        #Live IP Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="Live IP").count()
            list1.append(temp2)
        str1=map(str,list1)
        ip_ra=list(str1)

        #Shared Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="Shared").count()
            list1.append(temp2)
        str1=map(str,list1)
        shared_skif=list(str1)
        #Shared Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="Shared").count()
            list1.append(temp2)
        str1=map(str,list1)
        shared_ra=list(str1)

        # BP Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="Business Plus").count()
            list1.append(temp2)
        str1=map(str,list1)
        bp_skif=list(str1)
        #BP Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="Business Plus").count()
            list1.append(temp2)
        str1=map(str,list1)
        bp_ra=list(str1)

        # L2 Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="L2 Data").count()
            list1.append(temp2)
        str1=map(str,list1)
        l2_skif=list(str1)
        #L2 Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="L2 Data").count()
            list1.append(temp2)
        str1=map(str,list1)
        l2_ra=list(str1)

        # VPS Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="VPS").count()
            list1.append(temp2)
        str1=map(str,list1)
        vps_skif=list(str1)
        #VPS Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="VPS").count()
            list1.append(temp2)
        str1=map(str,list1)
        vps_ra=list(str1)

        # Hosted Count Per City skif
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='SKIF').filter(city=city).filter(service_subscribed__service_type__startswith="Hosted Server").count()
            list1.append(temp2)
        str1=map(str,list1)
        hosted_skif=list(str1)
        #Hosted Count Per City RA
        list1=[]
        str1=" "
        for city in cities_list:
            temp2=Customer.objects.all().filter(status='Active').filter(billing_company='RA').filter(city=city).filter(service_subscribed__service_type__startswith="Hosted Server").count()
            list1.append(temp2)
        str1=map(str,list1)
        hosted_ra=list(str1)

        total_cities=[]
        total_revenue_city=[]
        total_city=0
        for city in cities_list:
            total_cities.append(city)
            for customer in Customer.objects.all().filter(status='Active'):
                if customer.city ==city:
                    total_city+=customer.total_billing1()
            total_revenue_city.append(total_city)
            total_city=0

        #Total Customer Count
        customer_count=Customer.objects.all().filter(status='Active').count()

        #Total MBs Sold
        total_mbs=0

        temp2=Customer.objects.all().filter(status='Active')

        for customer in temp2:
            for service in customer.service_subscribed.all():
                if re.search("CIR", service.service_type) or re.search("Shared", service.service_type) or re.search("Business", service.service_type) or re.search("L2", service.service_type):
                    total_mbs+=service.service_qunatity



    #Total Revenue
        total_grand=0
        for customer in Customer.objects.all().filter(status='Active'):
            total_grand+=customer.total_billing1()







        context["qs"]=Customer.objects.all()
        context["qs1"]=Service.objects.all()
        context["qs2"]=Invoice.objects.all()
        context["data_ra"]=ra_count_per_city
        context["data_skif"]=skif_count_per_city
        context["skif_revenue_per_city"]=skif_revenue_per_city
        context["ra_revenue_per_city"]=ra_revenue_per_city
        context["services"]=services
        context["service_count_skif"]=skif_service_count
        context["service_count_ra"]=ra_service_count
        context["cities"]=cities_list
        context["cir_skif"]=cir_skif
        context["cir_ra"]=cir_ra
        context["ip_skif"]=ip_skif
        context["ip_ra"]=ip_ra
        context["shared_skif"]=shared_skif
        context["shared_ra"]=shared_ra
        context["bp_skif"]=bp_skif
        context["bp_ra"]=bp_ra
        context["l2_skif"]=l2_skif
        context["l2_ra"]=l2_ra
        context["vps_skif"]=vps_skif
        context["vps_ra"]=vps_ra
        context["hosted_skif"]=hosted_skif
        context["hosted_ra"]=hosted_ra
        context["total_cities"]=total_cities
        context["total_revenue_city"]=total_revenue_city
        context["customer_count"]=customer_count
        context["total_grand"]=total_grand
        context["total_mbs"]=total_mbs
        context["total_mbs"]=total_mbs

        return context

class TestPage(TemplateView):
    template_name='test.html'

class ThanksPage(TemplateView):
    template_name='thanks.html'
