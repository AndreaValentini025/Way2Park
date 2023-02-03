from django.db import models

# Create your models here.


class Parcheggio(models.Model):
    indirizzo = models.CharField(max_length=100)
    capienza = models.PositiveIntegerField()
    occupazione = models.PositiveIntegerField()
    costo = models.DecimalField(max_digits=5, decimal_places=2)
    lat = models.DecimalField(max_digits=17, decimal_places=15)
    long = models.DecimalField(max_digits=17, decimal_places=15)
    #44.69484259368893, 10.626217785348512

    def __str__(self):
        return 'Parcheggio ' + self.indirizzo

    def p_liberi(self):
        return self.capienza - self.occupazione


class MetodoPagamento(models.Model):
    carta = models.CharField(max_length=16, unique=True)
    saldo = models.DecimalField(default=50, decimal_places=2, max_digits=5)

    def pagamento(self,spesa):
        self.saldo -= spesa


class Targa(models.Model):
    targa = models.CharField(max_length=7, unique=True)
    metodo_pagamento = models.ForeignKey(MetodoPagamento, on_delete=models.CASCADE, null=True)


class Posteggio(models.Model):
    parcheggio = models.ForeignKey(Parcheggio, on_delete=models.DO_NOTHING)
    targa = models.ForeignKey(Targa, on_delete=models.DO_NOTHING)
    ingresso = models.DateTimeField(auto_now_add=True)
    uscita = models.DateTimeField(auto_now=True)
    pagamento = models.BooleanField(default=False)

