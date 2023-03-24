from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import cheque_bancario, cuentas_contables, cuenta, Usuario
import datetime
from django.db.models import F
import uuid
from django.db.models import Q


# Create your views here.

now = datetime.date.today()
print(now)


def index(request):
    logout(request)
    return render(request, "index.html")


def login(request):
    if request.method == "POST":
        enteredUser = request.POST["username"]
        enteredPassword = request.POST["password1"]
        user = authenticate(
            username=request.POST["username"].lower(), password=request.POST["password1"])

        print(user)
        print(request.POST, enteredPassword)

        if user is not None:
            auth_login(request, user)
            return redirect(f"/userLogged/{user}")
        else:
            return render(request, "login/login.html", {
                "error": "Usuario o contraseña incorrectos"
            })

    elif request.method == "GET":
        return render(request, "login/login.html")


@login_required
def userLogged(request, user):
    print (user)
    if Usuario.objects.filter(username=user).exists():
        userC = Usuario.objects.get(username=user)
        accounts = cuenta.objects.filter(cta_owner=userC.userCIF)
        cuentasTerceros= cuenta.objects.filter(~Q(cta_owner=userC.userCIF))
        print(cuenta.objects.filter(cta_owner=userC.userCIF))
        
        return render(request, 'userLogged/userLogged.html', {
            "user": user,
            "accounts": accounts,
            "date": now
        })
    else:
        return HttpResponse("noexiste")


@login_required
def signout(request):
    logout(request)
    return redirect("login")


def signup(request):
    logout(request)
    if request.method == "GET":
        print("enviando datos")
        return render(request, "signup/signup.html", {
            "form": UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            username = request.POST["username"]
            email = request.POST["email"]
            if Usuario.objects.filter(username=username).exists():
                return render(request, "signup/signup.html", {
                    "userTaken": "Usuario ya existe"
                })
            elif Usuario.objects.filter(user_email=email).exists():
                return render(request, "signup/signup.html", {
                    "emailTaken": "Email ya existe"
                })
            elif Usuario.objects.filter(userCIF=request.POST["ID"]).exists():
                return render(request, "signup/signup.html", {
                    "idExist": "ID ya esta asociado a otro usuario"
                })
            else:

                new_usuario = Usuario.objects.create(
                    username=request.POST['username'],
                    user_password=request.POST['password1'],
                    user_email=request.POST["email"],
                    userCIF=request.POST["ID"],
                    user_name=request.POST["name"],
                    user_lastName=request.POST["last_name"]
                )

                new_usuario.save()

                return redirect("login")
        else:
            return render(request, "signup/signup.html", {
                "error": "passwords do not match"
            })




def ck(request):
    ckd = cheque_bancario.objects.all()
    if request.method == "POST":
        try:
            ck = cheque_bancario.objects.create(
                ck_number=request.POST["ck_numero"],
                ck_amount=request.POST["ck_monto"],
                ck_beneficiario=request.POST["ck_beneficiario"],
                ck_remitente=request.POST["ck_remitente"],
                ck_descripcion=request.POST["ck_descripcion"],
                ck_status=False,
                ck_date=now
            )
            cuentas_contables.objects.filter(cc_name="PAGO CK BANCA PERSONAL").update(
                cc_balance=F('cc_balance') + ck.ck_amount)
            ck.save()
            return redirect("ck")
        except:
            print("exept")
            return render(request, "ck/ck.html", {
                "error": "Cheque ya existe",
                "ckd": ckd
            })

    else:
        return render(request, "ck/ck.html", {
            "ckd": ckd
        })


@login_required
def paycheck(request, ck_number):
    ckamount = cheque_bancario.objects.all()
    ccb = cuentas_contables.objects.all()
    ck_amount = cheque_bancario.objects.get(pk=ck_number).ck_amount

    print(ck_amount)

    if request.method == "POST":
        if cheque_bancario.objects.get(pk=ck_number).ck_status != True:
            print(ccb.filter(cc_name="PAGO CK BANCA PERSONAL").update(
                cc_balance=F('cc_balance') - ck_amount))
            cheque_bancario.objects.filter(pk=ck_number).update(ck_status=True)
            return redirect("ck")
        else:
            print(cuenta.objects.get(pk=ck_number).aho_balance)
            return redirect("ck")

    else:
        return HttpResponse("get")


def cuentas(request):
    cuentas = cuenta.objects.all()
    if request.method == "GET":
        return render(request, "cuentas/cuentas.html", {"cuentas": cuentas})


@login_required
def crearCuenta(request, user):
    if request.method == "GET":
        return render(request, "crearCuenta/crearCuenta.html")
    else:
        print(request.POST)
        print(Usuario.objects.get(username=user).username)

        new_cuenta = cuenta.objects.create(
            cta_type=request.POST['cta_type'],
            cta_moneda=request.POST['cta_moneda'],
            cta_name=Usuario.objects.get(username=user).user_name,
            cta_owner=Usuario.objects.get(username=user)
        )

        new_cuenta.save()

        return redirect(f"/userLogged/{user}", {
            "succesfull": "nueva cuenta creada"
        })


def deposito(request, cta_number,user):
    cuentas = cuenta.objects.all()
    if request.method == "GET":
        return render(request, "deposito/deposito.html", {
            "cta_number": cta_number,
            "user":user
        })


def depositar(request, cta_number,user):
    cuentas = cuenta.objects.all()
    if request.method == "POST":
        amount = request.POST["dep_monto"]
        cuenta.objects.filter(pk=cta_number).update(
            cta_balance=F('cta_balance')+amount)
        print(cuenta.objects.get(pk=cta_number), amount)
        print(amount)
        return redirect(f"/userLogged/{user}", {
                        "user": user})


@login_required
def transferirEntreMisCuentas(request, user):
    usuario = Usuario.objects.get(username=user)
    userC = Usuario.objects.get(username=user)
    accounts = cuenta.objects.filter(cta_owner=userC.userCIF)
    if request.method == "GET":
        print(request.method)
        return render(request, "transferirEntreMisCuentas/transferirEntreMisCuentas.html", {      
            "accounts": accounts,
            "user": user,
        })
    else:

        FromCtaBalance = cuenta.objects.get(cta_number=request.POST["from_account"]).cta_balance
        ToCtaBalance = cuenta.objects.get(cta_number=request.POST["to_account"]).cta_balance
        FromCtaMoneda = cuenta.objects.get(cta_number=request.POST["from_account"]).cta_moneda
        ToCtaMoneda = cuenta.objects.get(cta_number=request.POST["to_account"]).cta_moneda
        TransferAmount = request.POST["transfer_amount"]

        
        if FromCtaMoneda != ToCtaMoneda:
            return render(request, "transferirEntreMisCuentas/transferirEntreMisCuentas.html", {
                "error": "Moneda incompatible",
                "accounts": accounts,
                "user": user
            })
        elif len(TransferAmount) == 0:
            return render(request, "transferirEntreMisCuentas/transferirEntreMisCuentas.html", {
                "error": "Ingrese un monto valido",
                "accounts": accounts,
                "user": user
            })
        elif FromCtaBalance < int(TransferAmount):
            return render(request, "transferirEntreMisCuentas/transferirEntreMisCuentas.html", {
                "error": "Monto Insuficiente",
                "accounts": accounts,
                "user": user
            })
        else:
            cuenta.objects.filter(cta_number=request.POST["from_account"]).update(cta_balance=F('cta_balance')-TransferAmount)
            cuenta.objects.filter(cta_number=request.POST["to_account"]).update(cta_balance=F('cta_balance')+TransferAmount)
            return redirect(f"/userLogged/{user}", {
                            "user": user})
