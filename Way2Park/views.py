from datetime import datetime, date, time

import django.core.exceptions
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Parcheggio, MetodoPagamento, Targa, Posteggio
from django.http import HttpResponse


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
            context = {'name': name}
            return render(request, 'Way2Park/hello.html', context)
    else:
        return redirect('index')


class ParcheggiListView(generic.ListView):
    model = Parcheggio
    template_name = 'Way2Park/homepage.html'
    context_object_name = 'lista_parcheggi'


def formAssociaTargaMP(request):
    return render(request, 'Way2Park/car-registration.html')


def associazione(request):
    carta, created = MetodoPagamento.objects.get_or_create(carta__exact=request.POST['ncarta'])
    carta.carta = request.POST['ncarta']
    carta.save()
    targa, created = Targa.objects.get_or_create(targa__exact=request.POST['ntarga'])
    targa.targa = request.POST['ntarga']
    targa.metodo_pagamento = carta
    print(targa.metodo_pagamento)
    targa.save()
    return redirect('homepage')


class AssociaTargaMPView(generic.CreateView):
    model = Targa


def createPosteggio(request):
    targa, created = Targa.objects.get_or_create(targa__exact=request.POST['ntarga'])
    parcheggio = Parcheggio.objects.get(id__exact=request.POST['park'])
    if created:
        targa.targa = request.POST['ntarga']
        targa.save()

    posteggio, created = Posteggio.objects.get_or_create(targa=targa, parcheggio=parcheggio, uscita__isnull=True)

    if created:
        posteggio.targa = targa
        posteggio.parcheggio = parcheggio
        posteggio.ingresso = datetime.now()
        posteggio.parcheggio.occupazione+=1
        posteggio.save()

        response = HttpResponse('INIZIO Posteggio registrato correttamente!')
        response.status_code = 210  # sample status code
        return response
    else:
        posteggio.uscita = datetime.now()
        tempo_post = posteggio.uscita - posteggio.ingresso
        posteggio.spesa = tempo_post.total_seconds().__floor__() * (posteggio.parcheggio.costo / 3600)
        if posteggio.targa.metodo_pagamento :
            posteggio.targa.metodo_pagamento.saldo -= posteggio.spesa
            posteggio.pagamento=True
            posteggio.parcheggio.occupazione -= 1
            posteggio.save()
            response = HttpResponse('TERMINE Posteggio registrato correttamente!')
            response.status_code = 211  # sample status code
            return response
        else:
            posteggio.pagamento = False
            posteggio.save()
            response = HttpResponse('Pagamento richiesto!')
            response.status_code = 212  # sample status code
            response.headers['Spesa'] = posteggio.spesa
            response.headers['id_post'] = posteggio.id
            return response

def payPosteggio(request):
    posteggio = Posteggio.objects.get(id__exact=request.POST["id_post"])
    posteggio.pagamento=True
    posteggio.parcheggio.occupazione -= 1
    posteggio.save()
    response = HttpResponse('Pagamento Posteggio registrato correttamente!')
    response.status_code = 213  # sample status code
    return response





