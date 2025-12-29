from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import FacturaFinal, Presupuesto, Reparacion
import os

# =============================
# Formulario de registro
# =============================
class RegistroForm(UserCreationForm):

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].help_text = ""
        self.fields["password1"].label = "Repetí tu usuario"
        self.fields["password1"].help_text = ""
        self.fields["password1"].widget = forms.TextInput()
        self.fields["password2"].label = "Confirmación"
        self.fields["password2"].help_text = "Usamos tu nombre de usuario"
        self.fields["password2"].widget = forms.TextInput()


# =============================
# Formulario de Reparación
# =============================
class ReparacionForm(forms.ModelForm):

    # -----------------------------
    # Opciones predefinidas
    # -----------------------------
    UBICACION_CHOICES = [
        ("", "Seleccioná una opción"),
        ("Dina Huapi", "Dina Huapi"),
        ("Zona Este", "Zona Este"),
        ("Centro", "Centro"),
        ("Zona Gutierrez", "Zona Gutierrez"),
        ("Km 3 al 8", "Km 3 al 8"),
        ("Km 9 al 18", "Km 9 al 18"),
        ("Km 19 al 26", "Km 19 al 26"),
        ("Circuito Chico", "Circuito Chico"),
        ("Otro", "Otro"),
    ]

    TIPO_EQUIPO_CHOICES = [
        ("", "Seleccioná una opción"),
        ("Surf", "Surf"),
        ("Kite", "Kite"),
        ("Foil", "Foil"),
        ("SUP", "SUP"),
        ("Accesorio", "Accesorio"),
        ("Otro", "Otro"),
    ]

    ubicacion = forms.ChoiceField(choices=UBICACION_CHOICES)
    tipo_equipo = forms.ChoiceField(choices=TIPO_EQUIPO_CHOICES)

    imagen2 = forms.ImageField(
        required=False,
        label="Segunda imagen (opcional)"
    )

    MAX_VIDEO_MB = 150

    class Meta:
        model = Reparacion
        fields = [
            "telefono",
            "ubicacion",
            "tipo_equipo",
            "descripcion",
            "imagen",
            "imagen2",
            "video",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["imagen"].required = True
        self.fields["video"].required = False
        self.fields["ubicacion"].initial = ""
        self.fields["ubicacion"].required = True
        self.fields["ubicacion"].widget.attrs.update({"required": "required"})
        self.fields["tipo_equipo"].initial = ""
        self.fields["tipo_equipo"].required = True
        self.fields["tipo_equipo"].widget.attrs.update({"required": "required"})

    def clean_ubicacion(self):
        ubicacion = self.cleaned_data.get("ubicacion")
        if not ubicacion:
            raise forms.ValidationError("Seleccioná una opción.")
        return ubicacion

    def clean_tipo_equipo(self):
        tipo_equipo = self.cleaned_data.get("tipo_equipo")
        if not tipo_equipo:
            raise forms.ValidationError("Seleccioná una opción.")
        return tipo_equipo

    def clean_video(self):
        video = self.cleaned_data.get("video")
        if not video:
            return video

        size_bytes = getattr(video, "size", 0) or 0
        size_mb = size_bytes / (1024 * 1024)

        if size_mb > self.MAX_VIDEO_MB:
            raise forms.ValidationError(
                f"El video pesa {size_mb:.1f}MB y supera el máximo permitido ({self.MAX_VIDEO_MB}MB)."
            )

        return video


class PresupuestoForm(forms.ModelForm):

    class Meta:
        model = Presupuesto
        fields = [
            "archivo_presupuesto",
            "monto",
            "moneda",
            "notas_internas",
        ]


class FacturaFinalForm(forms.ModelForm):
    class Meta:
        model = FacturaFinal
        fields = [
            "monto_total",
            "moneda",
            "archivo_factura",
            "link_factura",
            "notas_internas",
        ]
        labels = {
            "monto_total": "Monto total",
            "moneda": "Moneda",
            "archivo_factura": "Archivo de factura (PDF o imagen)",
            "link_factura": "o Link de factura",
            "notas_internas": "Notas internas",
        }

    def clean(self):
        cleaned_data = super().clean()
        archivo = cleaned_data.get("archivo_factura")
        link = cleaned_data.get("link_factura")

        if not archivo and not link:
            raise forms.ValidationError(
                "Tenés que cargar un archivo o pegar un link para la factura final."
            )

        if archivo:
            ext = os.path.splitext(archivo.name)[1].lower().lstrip(".")
            if ext not in {"pdf", "jpg", "jpeg", "png"}:
                self.add_error(
                    "archivo_factura",
                    "Formato inválido. Usá PDF o imagen (JPG/PNG).",
                )
        return cleaned_data
