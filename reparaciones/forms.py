from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Reparacion
from django.core.exceptions import ValidationError

# =============================
# Formulario de registro
# =============================
class RegistroForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Quitamos el help_text de username
        self.fields['username'].help_text = ""

# =============================
# Formulario de Reparación
# =============================
class ReparacionForm(forms.ModelForm):

    # -----------------------------
    # Opciones predefinidas
    # -----------------------------
    UBICACION_CHOICES = [
        ('Dina Huapi', 'Dina Huapi'),
        ('Zona Este', 'Zona Este'),
        ('Centro', 'Centro'),
        ('Zona Gutierrez', 'Zona Gutierrez'),
        ('Km 3 al 8', 'Km 3 al 8'),
        ('Km 9 al 18', 'Km 9 al 18'),
        ('Km 19 al 26', 'Km 19 al 26'),
        ('Circuito Chico', 'Circuito Chico'),
        ('Otro', 'Otro'),
    ]

    TIPO_EQUIPO_CHOICES = [
        ('Surf', 'Surf'),
        ('Kite', 'Kite'),
        ('Foil', 'Foil'),
        ('SUP', 'SUP'),
        ('Accesorio', 'Accesorio'),
        ('Otro', 'Otro'),
    ]

    # -----------------------------
    # Campos adicionales
    # -----------------------------
    imagen2 = forms.ImageField(
        required=False,
        label="Segunda imagen (opcional)"
    )

    def clean_video(self):
        video = self.cleaned_data.get("video")
        if not video:
            return video

        size_bytes = getattr(video, "size", 0) or 0
        size_mb = size_bytes / (1024 * 1024)
        max_bytes = self.MAX_VIDEO_MB * 1024 * 1024  # 150MB reales

        if size_bytes > max_bytes:
            raise forms.ValidationError(
                f"El video pesa {size_mb:.1f}MB y supera el máximo permitido ({self.MAX_VIDEO_MB}MB)."
            )

        return video



    ubicacion = forms.ChoiceField(choices=UBICACION_CHOICES)
    tipo_equipo = forms.ChoiceField(choices=TIPO_EQUIPO_CHOICES)

    orden_usuario = forms.IntegerField(
        label="Prioridad de atención",
        required=False,
        min_value=1,
        help_text="1 = se hace primero. Solo visible si tenés más de una reparación y el estado permite cambios."
    )

    class Meta:
        model = Reparacion
        fields = [
            'nombre_cliente',
            'telefono',
            'ubicacion',
            'tipo_equipo',
            'descripcion',
            'imagen',
            'imagen2',
            'video',
            'orden_usuario',
        ]

    # =============================
    # Lógica del formulario
    # =============================
    MAX_VIDEO_MB = 150

    def __init__(self, *args, **kwargs):
        """
        user se pasa desde la view para:
        - calcular prioridad automática
        - bloquear edición cuando no corresponde
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["imagen"].required = True
        self.fields["video"].required = False

        # Si es creación nueva
        if not self.instance.pk and self.user:
            cantidad = Reparacion.objects.filter(usuario=self.user).count()

            if cantidad == 0:
                # Primera reparación: no mostrar prioridad
                self.fields['orden_usuario'].widget = forms.HiddenInput()
                self.initial['orden_usuario'] = 1
            else:
                # Mostrar campo para asignar prioridad
                self.initial['orden_usuario'] = cantidad + 1

        # Si es edición existente
        if self.instance.pk:
            if not self.instance.puede_editar_prioridad():
                self.fields['orden_usuario'].disabled = True

    def clean_orden_usuario(self):
        """
        Validación final de prioridad.
        """
        orden = self.cleaned_data.get('orden_usuario')

        if not orden:
            # Mantener valor actual si no se modificó
            return self.instance.orden_usuario or 1

        return orden
