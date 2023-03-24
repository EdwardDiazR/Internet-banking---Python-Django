from django.contrib import admin
from .models import Usuario,cheque_bancario ,cuentas_contables ,cuenta



# Register your models here.
admin.site.register(cheque_bancario)
admin.site.register(cuentas_contables)
admin.site.register(cuenta)
admin.site.register(Usuario)

