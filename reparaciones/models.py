from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


ESTADOS = [
    ("recibida", "Recibimos tu solicitud"),
    ("pendiente_presupuesto", "Estamos presupuestando el pedido"),
    ("pendiente_pago", "Estamos a espera de tu aprobación y pago de seña"),
    ("en_proceso", "En proceso de reparación"),
    ("listo_para_entregar", "Listo para entregar"),
    ("entregado", "Recibido por el cliente"),
    ("finalizado", "Recibimos el pago final"),
]


class Reparacion(models.Model):
    # -----------------------------
    # Datos del cliente
    # -----------------------------
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=200, blank=True)
    tipo_equipo = models.CharField(max_length=50)
    descripcion = models.TextField()

    # -----------------------------
    # Archivos enviados por el cliente
    # -----------------------------
    imagen = models.ImageField(upload_to="reparaciones/")
    imagen2 = models.ImageField(upload_to="reparaciones/", blank=True, null=True)
    video = models.FileField(
        upload_to="reparaciones/videos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mov", "mp4", "webm"])],
    )

    # -----------------------------
    # Estado del proceso
    # -----------------------------
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default="recibida",
    )

    # -----------------------------
    # Presupuesto (TALLER)
    # -----------------------------
    presupuesto_monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Monto del presupuesto en pesos",
    )

    presupuesto_detalle = models.TextField(
        blank=True,
        null=True,
        help_text="Detalle del presupuesto o aclaraciones",
    )

    presupuesto_archivo = models.FileField(
        upload_to="reparaciones/presupuestos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["pdf", "jpg", "jpeg", "png"])],
        help_text="Archivo adjunto del presupuesto (PDF o imagen)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    fecha_estimada_entrega = models.DateField(
        blank=True,
        null=True,
    )

    # -------------------
