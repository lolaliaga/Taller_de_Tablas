from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.urls import NoReverseMatch

from .forms import RegistroForm, ReparacionForm
from .models import Reparacion
from django.contrib.auth.views import LoginView
import logging

logger = logging.getLogger(__name__)

# -----------------------------
# Registro de usuario
# -----------------------------
def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            if form.is_valid():
                try:
                    reparacion = form.save(commit=False)
                    reparacion.usuario = request.user
                    reparacion.save()
                except Exception:
                    logger.exception("Error al guardar reparación")
                    raise

            # Asegura autenticación correcta (evita errores de backend)
            raw_password = form.cleaned_data.get("password1")
            authed_user = authenticate(
                request, username=user.username, password=raw_password
            )
            login(request, authed_user or user)

            # Evita 500 si la URL name 'inicio' no existe
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
    if request.method == 'POST':
        form = ReparacionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            reparacion = form.save(commit=False)
            reparacion.usuario = request.user
            reparacion.save()
            return redirect('inicio')
    else:
        form = ReparacionForm(user=request.user)

    return render(request, 'reparaciones/crear_reparacion.html', {'form': form})


# -----------------------------
# Dashboard de usuario
# -----------------------------

@login_required
def crear_reparacion(request):
    if request.method == 'POST':
        form = ReparacionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            try:
                reparacion = form.save(commit=False)
                reparacion.usuario = request.user
                reparacion.save()
                return redirect('inicio')
            except Exception as e:
                # En vez de 500, lo mostramos en el formulario
                logger.exception("Error guardando reparación")
                form.add_error(None, f"Error al guardar/subir archivos: {type(e).__name__}: {e}")
        # si no es válido, cae y re-renderiza con errores
    else:
        form = ReparacionForm(user=request.user)

    return render(request, 'reparaciones/crear_reparacion.html', {'form': form})


# -----------------------------
# Login personalizado con "Remember me"
# -----------------------------
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # La sesión expira al cerrar el navegador
            self.request.session.set_expiry(0)
        else:
            # Usa la duración por defecto de SESSION_COOKIE_AGE
            self.request.session.set_expiry(None)
        return super().form_valid(form)
