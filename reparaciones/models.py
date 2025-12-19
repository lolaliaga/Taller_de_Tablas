from django.db import models
from django.contrib.auth.models import User

ESTADOS = [
    ('pendiente_presupuesto', 'Estamos presupuestando el pedido'),
    ('pendiente_pago', 'Estamos a espera de tu aprobación y pago de seña'),
    ('en_proceso', 'En proceso de reparación'),
    ('listo_para_entregar', 'Listo para entregar'),
    ('entregado', 'Recibido por el cliente'),
    ('finalizado', 'Recibimos el pago final'),
]

PRIORIDADES = [
    (1, 'Alta'),
    (2, 'Media'),
    (3, 'Baja'),
]

ESTADOS_EDITABLES_PRIORIDAD = [
    'pendiente_presupuesto',
    'pendiente_pago',
]

class Reparacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    ubicacion = models.CharField(max_length=200, blank=True)
    tipo_equipo = models.CharField(max_length=50)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='reparaciones/')
    imagen2 = models.ImageField(upload_to='reparaciones/', blank=True, null=True)
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default='pendiente_presupuesto'
    )
    orden_usuario = models.PositiveIntegerField(
        default=1,
        help_text="Prioridad de atención: 1 = más alta"
    )
    fecha_finalizacion = models.DateField(blank=True, null=True)
    comentario_admin = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def puede_editar_prioridad(self):
        """
        Solo se puede editar la prioridad si el estado
        permite cambios y el usuario tiene más de una reparación.
        """
        if self.estado not in ESTADOS_EDITABLES_PRIORIDAD:
            return False
        cantidad = Reparacion.objects.filter(usuario=self.usuario).count()
        return cantidad > 1

    def __str__(self):
        return f"{self.tipo_equipo} - {self.nombre_cliente}"
