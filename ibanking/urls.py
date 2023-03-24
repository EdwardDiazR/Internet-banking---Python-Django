from django.urls import path
from . import views
from .models import cheque_bancario


urlpatterns=[
    path("", views.login,name="index"),
    path("login/",views.login,name="login"),
    path("signup",views.signup,name="signup"),
    path("ck",views.ck,name="ck"),
    path("paycheck/<int:ck_number>",views.paycheck,name="paycheck"),
    path("cuentas",views.cuentas,name="cuentas"),
    path("userLogged/<str:user>/deposito/<int:cta_number>",views.deposito,name="deposito"),
    path("userLogged/<str:user>/deposito/<int:cta_number>/depositar",views.depositar,name="depositar"),
    path("userLogged/<str:user>", views.userLogged,name="userLogged"),
    path("logout/",views.signout,name="logout"),
    path("userLogged/<str:user>/crearCuenta/",views.crearCuenta,name="crearCuenta"),
    path("userLogged/<str:user>/transferirAmiscuentas/",views.transferirEntreMisCuentas,name="transferirEntreMisCuentas")
]