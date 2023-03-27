from django.db import models
from django.contrib.auth import get_user_model
import datetime
import uuid

User = get_user_model()
print(User.last_login)

# Create your models here.

class Usuario(models.Model):
    userCIF = models.IntegerField(primary_key=True, unique=True,blank=False)
    username = models.CharField(max_length=100,unique=True)
    user_name= models.CharField(max_length=100,default="",blank=False)
    user_lastName= models.CharField(max_length=100 ,default="",blank=False)
    user_email= models.EmailField(max_length=100,blank=True)
    user_password= models.CharField(max_length=100)
    user_phone=models.CharField(max_length=12)
    user_role=models.CharField(max_length=100)

    def __str__(self):
        return self.username

class cuenta(models.Model):
    cta_number =  models.AutoField(auto_created = True,
                  primary_key = True,
                  serialize = False, 
                  verbose_name ='cta_number',
                  unique=True)
    cta_type = models.CharField(max_length=100)
    cta_moneda = models.CharField(max_length=3)
    cta_flotacion = models.FloatField(default=0)
    cta_bloqueos = models.FloatField(default=0)
    cta_balance = models.FloatField(default=0)
    cta_name = models.CharField(max_length=100, default="")
    cta_created = models.DateTimeField(auto_now_add=True)
    cta_owner = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    
    def __str__(self):
        return str(self.cta_number)

class Beneficiario(models.Model):
    benef_number = models.IntegerField()
    benef_name = models.CharField(max_length=100 ,default="")
    benef_owner = models.CharField(max_length=100)

        
    def __str__(self):
        return str(str(self.benef_number) + " " + str(self.benef_name))

class cheque_bancario(models.Model):
    ck_number = models.PositiveIntegerField(primary_key=True,editable=False, unique=True,auto_created=True)
    ck_amount = models.FloatField(max_length=100)
    ck_status = models.BooleanField(blank=False)
    ck_beneficiario = models.CharField(max_length=100, default="")
    ck_remitente = models.CharField(max_length=100,default="")
    ck_descripcion = models.CharField(max_length=100,default="")
    ck_date = models.DateTimeField(auto_now_add=True)

class cuentas_contables(models.Model):
    cc_id=models.UUIDField(primary_key=True, unique=True,default=uuid.uuid4,editable=False)
    cc_name=models.CharField(max_length=100)
    cc_balance=models.FloatField(default=0)

    def __str__(self):
        return self.cc_name
    

  
    
    

    