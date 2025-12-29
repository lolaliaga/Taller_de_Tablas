from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError, ObjectDoesNotExist


ESTADOS = [
    ("recibida", "Recibimos tu solicitud"),
    ("pendiente_presupuesto", "Estamos presupuestando el pedido"),
    ("pendiente_pago", "Estamos a espera de tu aprobación y pago de seña"),
    ("en_proceso", "En proceso de reparación"),
    ("listo_para_entregar", "Listo para entregar"),
    ("entregado", "Recibido por el cliente"),
    ("finalizado", "Recibimos el pago final"),
]

ESTADOS_PRESUPUESTO = [
    ("pendiente", "Pendiente"),
    ("enviado", "Enviado"),
    ("aprobado", "Aprobado"),
    ("rechazado", "Rechazado"),
]

MAX_PRESUPUESTO_MB = 20
MAX_FACTURA_MB = 20


def validar_tamano_presupuesto(archivo):
    size_bytes = getattr(archivo, "size", 0) or 0
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_PRESUPUESTO_MB:
        raise ValidationError(
            f"El archivo pesa {size_mb:.1f}MB y supera el máximo permitido ({MAX_PRESUPUESTO_MB}MB)."
        )


def validar_tamano_factura(archivo):
    size_bytes = getattr(archivo, "size", 0) or 0
    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_FACTURA_MB:
        raise ValidationError("El archivo supera el tamaño máximo permitido.")


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

    created_at = models.DateTimeField(auto_now_add=True)

    fecha_estimada_entrega = models.DateField(
        blank=True,
        null=True,
    )

    # -------------------
    @property
    def factura_final_safe(self):
        try:
            return self.factura_final
        except ObjectDoesNotExist:
            return None


class Presupuesto(models.Model):
    MONEDA_CHOICES = [
        ("ARS", "ARS"),
        ("USD", "USD"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="presupuestos",
    )
    reparacion = models.ForeignKey(
        Reparacion,
        on_delete=models.CASCADE,
        related_name="presupuestos",
    )
    archivo_presupuesto = models.FileField(
        upload_to="reparaciones/presupuestos/",
        validators=[validar_tamano_presupuesto],
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_PRESUPUESTO,
        default="pendiente",
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto final del presupuesto",
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default="ARS",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    notas_internas = models.TextField(blank=True)

    class Meta:
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Presupuesto #{self.pk} - Reparación #{self.reparacion_id}"


class FacturaFinal(models.Model):
    MONEDA_CHOICES = [
        ("ARS", "ARS"),
        ("USD", "USD"),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="facturas_finales",
    )
    reparacion = models.OneToOneField(
        Reparacion,
        on_delete=models.CASCADE,
        related_name="factura_final",
    )
    monto_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monto total facturado",
    )
    moneda = models.CharField(
        max_length=3,
        choices=MONEDA_CHOICES,
        default="ARS",
    )
    archivo_factura = models.FileField(
        upload_to="reparaciones/facturas_finales/",
        validators=[validar_tamano_factura],
        blank=True,
        null=True,
    )
    link_factura = models.URLField(blank=True)
    notas_internas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Factura final #{self.pk} - Reparación #{self.reparacion_id}"
