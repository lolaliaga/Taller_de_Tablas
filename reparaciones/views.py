from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import NoReverseMatch
import logging

from .forms import RegistroForm, ReparacionForm
from .models import Reparacion

logger = logging.getLogger(__name__)


# -----------------------------
# Registro de usuario
# -----------------------------
def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Login robusto (asegura backend)
            raw_password = form.cleaned_data.get("password1")
            authed_user = authenticate(request, username=user.username, password=raw_password)
            login(request, authed_user or user)

            try:
                return redirect("inicio")
            except NoReverseMatch:
                return redirect("/")
    else:
        form = RegistroForm()

    return render(request, "reparaciones/registrar.html", {"form": form})


# -----------------------------
# Crear reparación
# -----------------------------
@login_required
def crear_reparacion(request):
    if request.method == "POST":
        form = ReparacionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                reparacion = form.save(commit=False)
                reparacion.usuario = request.user
                reparacion.save()
                return redirect("inicio")
            except Exception as e:
                logger.exception("Error al guardar reparación")
                form.add_error(None, f"Error al guardar/subir: {type(e).__name__}: {e}")
    else:
        form = ReparacionForm(user=request.user)

    return render(request, "reparaciones/crear_reparacion.html", {"form": form})


# -----------------------------
# Dashboard de usuario
# -----------------------------
@login_required
def inicio(request):
    reparaciones = Reparacion.objects.filter(usuario=request.user).order_by("-created_at")

    return render(request, "reparaciones/inicio.html", {"reparaciones": reparaciones})


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
