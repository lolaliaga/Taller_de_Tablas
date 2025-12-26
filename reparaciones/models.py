from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


ESTADOS = [
    ('recibida', 'Recibimos tu solicitud'),
    ('pendiente_presupuesto', 'Estamos presupuestando el pedido'),
    ('pendiente_pago', 'Estamos a espera de tu aprobación y pago de seña'),
    ('en_proceso', 'En proceso de reparación'),
    ('listo_para_entregar', 'Listo para entregar'),
    ('entregado', 'Recibido por el cliente'),
    ('finalizado', 'Recibimos el pago final'),
]


class Reparacion(models.Model):
    # Usuario del sistema
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    # Datos del cliente
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=200, blank=True)

    # Equipo
    tipo_equipo = models.CharField(max_length=50)
    descripcion = models.TextField()

    # Media enviada por el cliente
    imagen = models.ImageField(upload_to='reparaciones/')
    imagen2 = models.ImageField(upload_to='reparaciones/', blank=True, null=True)
    video = models.FileField(
        upload_to="reparaciones/videos/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["mov", "mp4", "webm"])],
    )

    # Estado del proceso
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default='recibida'
    )

    # 📅 Fecha estimada de entrega (calendario)
    fecha_estimada_entrega = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha estimada de finalización"
    )

    # 💰 Presupuesto
    presupuesto_monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Monto del presupuesto"
    )

    presupuesto_detalle = models.TextField(
        blank=True,
        null=True,
        help_text="Detalle del presupuesto"
    )

    presupuesto_archivo = models.FileField(
        upload_to="reparaciones/presupuestos/",
        blank=True,
        null=True,
        help_text="PDF o imagen del presupuesto"
    )

    # Comentarios internos del taller
    comentario_admin = models.TextField(blank=True, null=True)

    # Sistema
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_equipo} - {self.nombre_cliente}"
