import mimetypes
import os

from django.http import FileResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib import messages
import logging

from .forms import FacturaFinalForm, PresupuestoForm, RegistroForm, ReparacionForm
from django.db.models import Prefetch

from .models import FacturaFinal, Presupuesto, Reparacion

logger = logging.getLogger(__name__)

# -----------------------------
# Dashboard / Inicio
# -----------------------------
@login_required
def inicio(request):
    reparaciones = Reparacion.objects.filter(
        usuario=request.user
    ).select_related(
        "factura_final"
    ).prefetch_related(
        Prefetch("presupuestos", queryset=Presupuesto.objects.order_by("-fecha_creacion"))
    ).order_by("-created_at")

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
@login_required
def descargar_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(Presupuesto, pk=presupuesto_id)
    if not request.user.is_staff and presupuesto.reparacion.usuario != request.user:
        messages.error(request, "No tenés permisos para ver este archivo.")
        return redirect("inicio")
    archivo = presupuesto.archivo_presupuesto
    filename = os.path.basename(archivo.name)
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    descargar = request.GET.get("download") == "1"
    response = FileResponse(
        archivo.open("rb"),
        as_attachment=descargar,
        content_type=content_type,
    )
    disposition = "attachment" if descargar else "inline"
    response["Content-Disposition"] = f'{disposition}; filename="{filename}"'
    return response


def _staff_required(request, message="No tenés permisos para acceder a esta sección."):
    if not request.user.is_staff:
        messages.error(request, message)
        return False
    return True


@login_required
def staff_reparaciones(request):
    if not _staff_required(request):
        return redirect("inicio")

    presupuestos_prefetch = Prefetch(
        "presupuestos",
        queryset=Presupuesto.objects.order_by("-fecha_creacion"),
        to_attr="presupuestos_ordenados",
    )
    reparaciones = (
        Reparacion.objects.exclude(estado="finalizado")
        .select_related("factura_final")
        .prefetch_related(presupuestos_prefetch)
        .order_by("-created_at")
    )
    return render(
        request,
        "reparaciones/staff_reparaciones.html",
        {"reparaciones": reparaciones},
    )


@login_required
def staff_reparacion_detalle(request, reparacion_id):
    if not _staff_required(request):
        return redirect("inicio")

    presupuestos_prefetch = Prefetch(
        "presupuestos",
        queryset=Presupuesto.objects.order_by("-fecha_creacion"),
        to_attr="presupuestos_ordenados",
    )
    reparacion = get_object_or_404(
        Reparacion.objects.select_related("factura_final").prefetch_related(
            presupuestos_prefetch
        ),
        pk=reparacion_id,
    )
    return render(
        request,
        "reparaciones/staff_reparacion_detalle.html",
        {"reparacion": reparacion},
    )


@login_required
def staff_finalizar_reparacion(request, reparacion_id):
    if not _staff_required(request, "No tenés permisos para finalizar esta reparación."):
        return redirect("inicio")

    reparacion = get_object_or_404(Reparacion, pk=reparacion_id)
    if request.method == "POST":
        reparacion.estado = "finalizado"
        reparacion.save(update_fields=["estado"])
        messages.success(
            request,
            "Trabajo finalizado. Ahora podés cargar la factura final.",
        )
    return redirect("staff_factura_final", reparacion_id=reparacion.id)


@login_required
def staff_cargar_presupuesto(request, reparacion_id):
    if not _staff_required(request):
        return redirect("inicio")

    reparacion = get_object_or_404(Reparacion, pk=reparacion_id)
    if request.method == "POST":
        form = PresupuestoForm(request.POST, request.FILES)
        if form.is_valid():
            presupuesto = form.save(commit=False)
            presupuesto.reparacion = reparacion
            presupuesto.usuario = request.user
            presupuesto.save()
            return redirect("staff_reparacion_detalle", reparacion_id=reparacion.id)
    else:
        form = PresupuestoForm()

    return render(
        request,
        "reparaciones/staff_presupuesto_form.html",
        {"form": form, "reparacion": reparacion},
    )


@login_required
def staff_presupuestos(request, reparacion_id):
    if not _staff_required(request):
        return redirect("inicio")

    reparacion = get_object_or_404(
        Reparacion.objects.prefetch_related(
            Prefetch("presupuestos", queryset=Presupuesto.objects.order_by("-fecha_creacion"))
        ),
        pk=reparacion_id,
    )
    return render(
        request,
        "reparaciones/staff_presupuestos.html",
        {"reparacion": reparacion},
    )


@login_required
def staff_factura_final(request, reparacion_id):
    if not _staff_required(request):
        return redirect("inicio")

    reparacion = get_object_or_404(Reparacion, pk=reparacion_id)
    factura = reparacion.factura_final_safe
    if request.method == "POST":
        form = FacturaFinalForm(request.POST, request.FILES, instance=factura)
        if form.is_valid():
            factura = form.save(commit=False)
            factura.reparacion = reparacion
            factura.usuario = request.user
            factura.save()
            messages.success(request, "Factura final guardada correctamente.")
            return redirect("staff_finalizados")
    else:
        form = FacturaFinalForm(instance=factura)

    return render(
        request,
        "reparaciones/staff_factura_final.html",
        {"form": form, "reparacion": reparacion},
    )


@login_required
def staff_finalizados(request):
    if not _staff_required(request):
        return redirect("inicio")

    presupuestos_prefetch = Prefetch(
        "presupuestos",
        queryset=Presupuesto.objects.order_by("-fecha_creacion"),
        to_attr="presupuestos_ordenados",
    )
    reparaciones = (
        Reparacion.objects.filter(estado="finalizado")
        .select_related("factura_final")
        .prefetch_related(presupuestos_prefetch)
        .order_by("-created_at")
    )
    return render(
        request,
        "reparaciones/staff_finalizados.html",
        {"reparaciones": reparaciones},
    )


@login_required
def staff_reabrir_reparacion(request, reparacion_id):
    if not request.user.is_superuser:
        messages.error(request, "No tenés permisos para reabrir esta reparación.")
        return redirect("staff_finalizados")

    reparacion = get_object_or_404(Reparacion, pk=reparacion_id)
    if request.method == "POST":
        reparacion.estado = "en_proceso"
        reparacion.save(update_fields=["estado"])
    return redirect("staff_finalizados")


@login_required
def descargar_factura_final(request, reparacion_id):
    reparacion = get_object_or_404(Reparacion, pk=reparacion_id)
    if not request.user.is_staff and reparacion.usuario != request.user:
        messages.error(request, "No tenés permisos para ver este archivo.")
        return redirect("inicio")

    factura = reparacion.factura_final_safe
    if factura is None:
        messages.error(request, "No tenés permisos para ver este archivo.")
        return redirect("inicio")

    if factura.archivo_factura:
        archivo = factura.archivo_factura
        return FileResponse(
            archivo.open("rb"),
            as_attachment=True,
            filename=os.path.basename(archivo.name),
        )

    if factura.link_factura:
        return redirect(factura.link_factura)

    messages.error(request, "No tenés permisos para ver este archivo.")
    return redirect("inicio")
