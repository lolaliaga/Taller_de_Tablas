from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import NoReverseMatch
import logging

from .forms import RegistroForm, ReparacionForm
from .models import Reparacion

from django.http import HttpResponse #prueba issue 500

logger = logging.getLogger(__name__)

def inicio(request):
    return HttpResponse("OK HOME") ##prueba issue 500
# -----------------------------
# Registro de usuario
# -----------------------------
def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Forzar backend para evitar errores silenciosos
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)

            return redirect("inicio")
    else:
        form = RegistroForm()

    return render(request, "reparaciones/registrar.html", {"form": form})

# -----------------------------
# Crear reparación
# -----------------------------

@login_required
def crear_reparacion(request):
    if request.method == "POST":
        form = ReparacionForm(request.POST, request.FILES)
        if form.is_valid():
            reparacion = form.save(commit=False)
            reparacion.usuario = request.user
            reparacion.save()

            # ✅ REDIRECT CLAVE
            return redirect("inicio")

    else:
        form = ReparacionForm()

    return render(
        request,
        "reparaciones/crear_reparacion.html",
        {"form": form}
    )
# -----------------------------
# Dashboard de usuario
# -----------------------------
#@login_required

#def inicio(request):
 #   reparaciones = Reparacion.objects.filter(usuario=request.user).order_by("-created_at")
#
 #   return render(request, "reparaciones/inicio.html", {"reparaciones": reparaciones})

#@login_required
#def inicio(request):
#    return render(
#        request,
#        "reparaciones/inicio.html",
#        {"reparaciones": []}
#    )

def inicio(request):
    return render(request, "reparaciones/inicio.html", {"reparaciones": []})


# -----------------------------
# Login personalizado con "Remember me"
# -----------------------------
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")
        if not remember_me:
            self.request.session.set_expiry(0)     # expira al cerrar navegador
        else:
            self.request.session.set_expiry(None)  # default SESSION_COOKIE_AGE
        return super().form_valid(form)
