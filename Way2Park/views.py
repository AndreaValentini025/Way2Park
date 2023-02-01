from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from .models import Parcheggio

def index(request):
    print('Request for index page received')
    return render(request, 'Way2Park/index.html')

@csrf_exempt
def hello(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name is None or name == '':
            print("Request for hello page received with no name or blank name -- redirecting")
            return redirect('index')
        else:
            print("Request for hello page received with name=%s" % name)
            context = {'name': name }
            return render(request, 'Way2Park/hello.html', context)
    else:
        return redirect('index')


class ParcheggiListView(generic.ListView):
    model = Parcheggio
    template_name = 'Way2Park/homepage.html'
    context_object_name = 'lista_parcheggi'
