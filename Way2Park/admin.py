from django.contrib import admin
from .models import Parcheggio,MetodoPagamento,Targa,Posteggio
# Register your models here.
admin.site.register(Parcheggio)
admin.site.register(MetodoPagamento)
admin.site.register(Targa)
admin.site.register(Posteggio)