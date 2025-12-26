import os

from django.http import FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
import logging

from .forms import RegistroForm, ReparacionForm
from .models import Presupuesto, Reparacion

logger = logging.getLogger(__name__)

# -----------------------------
# Dashboard / Inicio
# -----------------------------
@login_required
def inicio(request):
    reparaciones = Reparacion.objects.filter(
        usuario=request.user
    ).prefetch_related("presupuestos").order_by("-created_at")

    return render(
        request,
        "reparaciones/inicio.html",
        {"reparaciones": reparaciones}
    )

# -----------------------------
# Registro de usuario
# -----------------------------
def registrar(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Login automático luego del registro
            login(request, user)

            return redirect("inicio")
    else:
        form = RegistroForm()

    return render(
        request,
        "reparaciones/registrar.html",
        {"form": form}
    )

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

            # 👉 volver al dashboard
            return redirect("inicio")
    else:
        form = ReparacionForm()

    return render(
        request,
        "reparaciones/crear_reparacion.html",
        {"form": form}
    )

# -----------------------------
# Login personalizado
# -----------------------------
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")

        if not remember_me:
            # sesión expira al cerrar el navegador
            self.request.session.set_expiry(0)
        else:
            # usa SESSION_COOKIE_AGE
            self.request.session.set_expiry(None)

        return super().form_valid(form)


@login_required
def descargar_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(
        Presupuesto,
        pk=presupuesto_id,
        reparacion__usuario=request.user,
    )
    archivo = presupuesto.archivo_presupuesto
    return FileResponse(
        archivo.open("rb"),
        as_attachment=True,
        filename=os.path.basename(archivo.name),
    )
