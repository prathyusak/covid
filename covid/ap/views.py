import matplotlib
matplotlib.use("Agg")
from django.shortcuts import render,HttpResponse
from .models import District
import pandas as pd
from pylab import *
from io import BytesIO
import base64
import matplotlib.ticker as ticker




# Create your views here.
def home(request):
    lastrow = District.objects.all().order_by('date').values('date')[::-1]
    dt = lastrow[0]['date']
    dists = District.objects.filter(date=dt).order_by('name')
    Total = sum(dist.count for dist in dists)
    Ttotal =  sum(dist.lcount for dist in dists)
    Recovered = sum(dist.recovered for dist in dists)
    Deceased = sum(dist.deceased for dist in dists)
    image1 = districtplot()
    image2 = daywise()
    return render(request,'index.html',{'dists':dists,'Total':Total,'Ttotal':Ttotal,'Recovered':Recovered,'Deceased':Deceased,'dt':dt,'image1':image1,'image2':image2})

def upload(request):
    import requests
    from bs4 import BeautifulSoup
    res = requests.get('http://hmfw.ap.gov.in/covid_dashboard.aspx')
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find_all("table", {"class": "table table-bordered table-striped"})
    rawdata = [[int(td.text.strip()) if td.text.strip().isdigit() else td.text.strip() for td in tr.find_all('td')] for tr in table[0].find_all('tr')]
    tag = soup.select('span[id^=lblLast_Update]')
    lastupdate = tag[0].string
    ldate = lastupdate[6:10] + '-' + lastupdate[3:5] + '-' + lastupdate[0:2]
    lastrow = District.objects.all().order_by('date').values('date')[::-1]
    dt = lastrow[0]['date']
    rawdata[11][0]='Vishakapatnam'
    if str(dt) == str(ldate):
        print("Data Upto date")
        return HttpResponse("Already upto date")
    else:
        for i in range(1,14):
            lastcount = District.objects.filter(name=rawdata[i][0],date=dt).values_list('count',flat=True)[0]
            d = District(name=rawdata[i][0],count=rawdata[i][1],recovered=rawdata[i][2],
                         deceased=rawdata[i][3],date=ldate,lcount=rawdata[i][1]-lastcount,
                         active=rawdata[i][1]-(rawdata[i][2]+rawdata[i][3]))
            d.save()
        return HttpResponse("Data Saved to database")

    return render(request,'result.html')

def districtplot():
    lastrow = District.objects.all().order_by('date').values('date')[::-1]
    dt = lastrow[0]['date']
    qs = District.objects.filter(date=dt).order_by('name').values_list('name','count','lcount')
    state_data = pd.DataFrame(data=qs,
                              columns=['District', 'Confirmed', 'New Cases'])
    state_data.set_index("District", inplace=True)
    plt.figure(figsize=(15, 15))
    state_data.plot.barh(stacked=True,align='center', color=['lightblue','red'])
    plt.gca().invert_yaxis()
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=5)
    for index, value in enumerate(state_data['Confirmed']):
        plt.text(value, index, str(value), fontsize=8)
    plt.title(f'Total Confirmed Cases Districtwise on {dt}', fontsize=10)
    grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    plt.close()
    return image_base64

def plot(request):
    if request.method == 'POST':
        plt.figure(figsize=(10, 10))
        district = request.POST['district']
        qs = District.objects.filter(name=district).values_list('name','count','date','lcount','active','deceased','recovered')
        dis_data = pd.DataFrame(data=qs,columns=['District','TotalConfirmed','date','New Cases','Hospitalised','Dead','Recovered'])
        dis_data = dis_data.sort_values(by=['date'])
        dis_data['date'] = pd.to_datetime(dis_data.date)
        dis_data['date'] = dis_data['date'].dt.strftime('%d/%m')
        dis_data.plot(x='date', y=['TotalConfirmed', 'New Cases', 'Recovered', 'Dead', 'Hospitalised'])
        grid(True)
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=14)
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        image1_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
        buf.close()
        plt.close()
        return render(request,'form.html',{'image1_base64':image1_base64,'district':district})
    else:
        ap= District.objects.all().values_list('name','count','date','lcount','active','deceased','recovered')
        ap_data = pd.DataFrame(data=ap, columns=['Name', 'TotalConfirmed', 'date', 'New Cases', 'Hospitalised', 'Dead', 'Recovered'])
        ap_data = ap_data.sort_values(by=['date'])
        ap_data = ap_data.groupby(['date']).sum()
        ap_data['date'] = pd.to_datetime(ap_data.index)
        ap_data['date'] = ap_data['date'].dt.strftime('%d/%m')
        ap_data.plot(x='date',y=['TotalConfirmed', 'New Cases', 'Recovered', 'Dead', 'Hospitalised'])
        plt.xticks(fontsize=10)
        plt.yticks(fontsize=14)
        grid(True)
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=300)
        image1_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
        buf.close()
        plt.close()

        return render(request, 'form.html',{'image1_base64':image1_base64,'district':'Andhra Pradesh'})


def daywise():
    ap_daywise = District.objects.all().values_list( 'date', 'lcount')
    daily_cases=pd.DataFrame(data=ap_daywise, columns=['date','New Cases'])
    daily_cases = daily_cases.groupby(['date']).sum()
    daily_cases['date']=pd.to_datetime(daily_cases.index)
    ax = daily_cases.plot(kind='bar',x='date',y='New Cases')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=14)
    plt.title(f'Daywise New Cases in Andhrapradesh', fontsize=10)
    ticklabels = daily_cases.date.dt.strftime('%d/%m')
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
    # show only each 30th label, another are not visible
    spacing = 5
    visible = ax.xaxis.get_ticklabels()[::spacing]
    for label in ax.xaxis.get_ticklabels():
        if label not in visible:
            label.set_visible(False)
    grid(True)
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    image1_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    plt.close()
    return image1_base64