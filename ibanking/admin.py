from django.contrib import admin
from .models import Usuario,cheque_bancario ,cuentas_contables ,cuenta,Beneficiario


# Register your models here.
admin.site.register(cheque_bancario)
admin.site.register(cuentas_contables)
admin.site.register(Beneficiario)
admin.site.register(cuenta)
admin.site.register(Usuario)

