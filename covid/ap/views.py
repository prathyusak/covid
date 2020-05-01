from django.shortcuts import render,HttpResponse
from .models import District
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
import io
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image
from io import BytesIO


# Create your views here.
def home(request):
    lastrow = District.objects.all().order_by('date').values('date')[::-1]
    dt = lastrow[0]['date']

    dists = District.objects.filter(date=dt).order_by('name')
    Total = sum(dist.count for dist in dists)
    Ttotal =  sum(dist.lcount for dist in dists)
    Recovered = sum(dist.recovered for dist in dists)
    Deceased = sum(dist.deceased for dist in dists)
    return render(request,'index.html',{'dists':dists,'Total':Total,'Ttotal':Ttotal,'Recovered':Recovered,'Deceased':Deceased,'dt':dt})

def upload(request):
    return render(request,'result.html')

def districtplot(response):
    lastrow = District.objects.all().order_by('date').values('date')[::-1]
    dt = lastrow[0]['date']
    qs = District.objects.filter(date=dt).order_by('name')
    q = qs.values('name', 'count')
    state_data = pd.DataFrame.from_records(q)
    print(state_data)
    plt.figure(figsize=(15, 10))
    plt.barh(state_data['name'], state_data['count'].map(int), align='center', color='lightblue',
             edgecolor='blue')
    plt.xlabel('No. of Confirmed cases', fontsize=18)
    plt.gca().invert_yaxis()
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    for index, value in enumerate(state_data['count']):
        plt.text(value, index, str(value), fontsize=12)
    #plt.show()
    grid(True)

    # Store image in a string buffer
    buffer = BytesIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pilImage = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    #pylab.close()

    # Send buffer in a http response the the browser with the mime type image/png set
    return HttpResponse(buffer.getvalue(), content_type="image/png")
