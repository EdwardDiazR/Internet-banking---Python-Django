from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import cheque_bancario, cuentas_contables, cuenta, Usuario, Beneficiario
import datetime
from django.db.models import F
import uuid
from django.db.models import Q
from .forms import SignUpForm, LoginForm
from django.contrib.auth.hashers import make_password,check_password
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.



now = datetime.date.today()
print(now)


def index(request):
    logout(request)
    return render(request, "index.html")


def login(request):
    form = LoginForm(request.POST)
    if request.method == "POST":
        if form.is_valid():
            enteredUser = request.POST["username"]
            enteredPassword = request.POST["password"]
            user = authenticate(
                username=form.cleaned_data["username"].lower(), password=form.cleaned_data["password"])

            print(user)
            print(LoginForm)
            print(request.POST, enteredPassword)

            if user is not None:
                auth_login(request, user)
                return redirect(f"/userLogged/{user}")
            else:
                return render(request, "login/login.html", {
                    "error": "Usuario o contraseña incorrectos",
                    "LForm": LoginForm
                })

    elif request.method == "GET":
        return render(request, "login/login.html", {

            "LForm": LoginForm
        })


@login_required
def userLogged(request, user):

    usuario = Usuario.objects.get(username=user)
    userC = Usuario.objects.get(username=user)
    accounts = cuenta.objects.filter(cta_owner=userC.userCIF)
    print(cuenta.objects.filter(cta_owner=userC.userCIF))
    for p in Usuario.objects.raw('SELECT userCIF FROM ibanking.ibanking_usuario WHERE username="adrian1"'):
        print(p)


    return render(request, 'userLogged/userLogged.html', {
        "usuario": usuario,
        "user": user,
        "accounts": accounts,
        "date": now
    })


@login_required
def signout(request):
    logout(request)
    return redirect("login")


def signup(request):
    logout(request)
    if request.method == "GET":
        return render(request, "signup/signup.html", {
            "form": SignUpForm,
        })
    elif request.method == "POST":
        h = SignUpForm(request.POST)
        if h.is_valid(): 
            user = User.objects.create_user(
                username=h.cleaned_data["username"])
            user.password = make_password(h.cleaned_data['user_password'])
            usuario = Usuario.objects.create(
                userCIF = h.cleaned_data["userCIF"],
                username = h.cleaned_data["username"].lower(),
                user_name = h.cleaned_data["user_name"],
                user_lastName = h.cleaned_data["user_lastName"],
                user_email=h.cleaned_data["user_email"],
                user_password = user.password,
                user_phone =h.cleaned_data["user_phone"]
            )
            usuario.save()
            user.save()
            return redirect("login")
        else:
            if Usuario.objects.filter(username=request.POST["username"]).exists():
                return render(request, "signup/signup.html", {
                    "error": "usuario ya existe",
                    "form": SignUpForm
                })
            elif request.POST["user_password"] != request.POST["confirm_pass"]:
                return render(request, "signup/signup.html", {
                    "error": "contraseñas no coinciden",
                    "form": SignUpForm
                })
            else:
                print(h)
                print(h.is_valid)
                print(h.is_valid())
                return HttpResponse("paso algo")


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
            cta_name=Usuario.objects.get(username=user).user_name + " " + Usuario.objects.get(username=user).user_lastName ,
            cta_owner=Usuario.objects.get(username=user)
        )

        new_cuenta.save()

        return redirect(f"/userLogged/{user}", {
            "succesfull": "nueva cuenta creada"
        })


def deposito(request, cta_number, user):
    cuentas = cuenta.objects.all()
    if request.method == "GET":
        return render(request, "deposito/deposito.html", {
            "cta_number": cta_number,
            "user": user,

        })


def depositar(request, cta_number, user):
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

        FromCtaBalance = cuenta.objects.get(
            cta_number=request.POST["from_account"]).cta_balance
        ToCtaBalance = cuenta.objects.get(
            cta_number=request.POST["to_account"]).cta_balance
        FromCtaMoneda = cuenta.objects.get(
            cta_number=request.POST["from_account"]).cta_moneda
        ToCtaMoneda = cuenta.objects.get(
            cta_number=request.POST["to_account"]).cta_moneda
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
            cuenta.objects.filter(cta_number=request.POST["from_account"]).update(
                cta_balance=F('cta_balance')-TransferAmount)
            cuenta.objects.filter(cta_number=request.POST["to_account"]).update(
                cta_balance=F('cta_balance')+TransferAmount)
            return redirect(f"/userLogged/{user}", {
                            "user": user})


@login_required
def beneficiarios(request, user):
    misBeneficiarios = Beneficiario.objects.filter(benef_owner=user)
    print(user)

    if request.method == "GET":
        return render(request, "beneficiarios/beneficiarios.html", {
            "beneficiarios": misBeneficiarios
        })

@login_required
def añadirBeneficiario(request, user):
        busqueda = request.GET.get("NumeroCuenta")
        cta = cuenta.objects.filter(cta_number=busqueda)

        print(Beneficiario.objects.filter(benef_owner=user))
        if request.method=="POST":
                if Beneficiario.objects.filter(benef_number=busqueda).exists():
                    return render(request,"añadirBeneficiario/añadirBeneficiario.html",{
                    "cuenta":cta,
                    "error":"Este beneficiario ya existe en su lista de beneficiarios"
                })
                else:
                    Beneficiario.objects.create(
                        benef_number=cuenta.objects.get(cta_number=cta.get().cta_number).cta_number,
                        benef_name=cuenta.objects.get(cta_number=cta.get().cta_number).cta_name ,
                        benef_owner= Usuario.objects.get(username=user).username
                )
                    return redirect(f"/userLogged/{user}/beneficiarios",{
                        "user": user
                    })

        else:
            if busqueda:
                return render(request,"añadirBeneficiario/añadirBeneficiario.html",{
                    "cuenta":cta
                })
            else:
            
                return render(request,"añadirBeneficiario/añadirBeneficiario.html")

       
    # cuentasTerceros = cuenta.objects.filter(~Q(cta_owner=userC.userCIF))


def eliminarBeneficiario():
    pass

def transferirAterceros(request, user):
    usuario = Usuario.objects.get(username=user)
    userC = Usuario.objects.get(username=user)
    myAccounts = cuenta.objects.filter(cta_owner=userC.userCIF)
    misBeneficiarios = Beneficiario.objects.filter(benef_owner=user)
    print(myAccounts)
    print(misBeneficiarios)
    if request.method == "GET":
        return render(request, "transferirAterceros/transferirAterceros.html", {
            "myAccounts": myAccounts,
            "misBeneficiarios": misBeneficiarios
        })
    else:
        FromCtaBalance = cuenta.objects.get(
            cta_number=request.POST["FromAccount"]).cta_balance
        ToCtaBalance = cuenta.objects.get(
            cta_number=request.POST["ToAccount"]).cta_balance
        FromCtaMoneda = cuenta.objects.get(
            cta_number=request.POST["FromAccount"]).cta_moneda
        ToCtaMoneda = cuenta.objects.get(
            cta_number=request.POST["ToAccount"]).cta_moneda
        TransferAmount = request.POST["transferAmount"]
        print(request.POST)
        print(FromCtaBalance)

        if FromCtaMoneda != ToCtaMoneda:
            return render(request, "transferirAterceros/transferirAterceros.html", {
                "myAccounts": myAccounts,
                "misBeneficiarios": misBeneficiarios

            })
        elif len(TransferAmount) == 0:
            return render(request, "transferirAterceros/transferirAterceros.html", {
                "myAccounts": myAccounts,
                "misBeneficiarios": misBeneficiarios

            })
        elif FromCtaBalance < int(TransferAmount):
            return render(request, "transferirAterceros/transferirAterceros.html", {
                "myAccounts": myAccounts,
                "misBeneficiarios": misBeneficiarios

            })
        else:
            cuenta.objects.filter(cta_number=request.POST["FromAccount"]).update(
                cta_balance=F('cta_balance')-TransferAmount)
            cuenta.objects.filter(cta_number=request.POST["ToAccount"]).update(
                cta_balance=F('cta_balance')+TransferAmount)
            return redirect(f"/userLogged/{user}", {
                            "user": user})


################## Unused for de moment ##########################
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


def cuentas(request):
    cuentas = cuenta.objects.all()
    if request.method == "GET":
        return render(request, "cuentas/cuentas.html", {"cuentas": cuentas})


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
