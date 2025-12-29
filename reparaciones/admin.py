from django.contrib import admin
from django.db import transaction
from django.db.models import Count, Max, Prefetch
from django.urls import reverse
from django.utils.formats import localize
from django.utils.html import format_html

from .models import Presupuesto, Reparacion


class PresupuestoInline(admin.TabularInline):
    model = Presupuesto
    extra = 0
    fields = (
        "archivo_presupuesto",
        "estado",
        "monto",
        "moneda",
        "fecha_creacion",
        "fecha_envio",
        "usuario",
        "notas_internas",
        "abrir_link",
    )
    readonly_fields = (
        "archivo_presupuesto",
        "estado",
        "monto",
        "moneda",
        "fecha_creacion",
        "fecha_envio",
        "usuario",
        "notas_internas",
        "abrir_link",
    )
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def abrir_link(self, obj):
        if not obj.pk:
            return "—"
        url = reverse("admin:reparaciones_presupuesto_change", args=[obj.pk])
        return format_html('<a href="{}">Abrir</a>', url)

    abrir_link.short_description = "Abrir"

@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre_cliente",
        "telefono",
        "ubicacion",
        "tipo_equipo",
        "estado",
        "presupuesto_resumen",
        "presupuestos_count",
        "ultimo_presupuesto_fecha",
        "ultimo_presupuesto_estado",
        "link_ultimo_presupuesto",
        "fecha_estimada_entrega",
        "usuario",
        "imagen_link",
        "video_link",
        "created_at",
    )
    list_filter = ('estado', 'tipo_equipo', 'usuario')
    search_fields = ('nombre_cliente', 'telefono', 'ubicacion', 'tipo_equipo')
    ordering = ('-id',)
    readonly_fields = ('usuario', 'tiene_video')  # El usuario que creó la reparación no se puede modificar desde el admin
    inlines = (PresupuestoInline,)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        presupuestos_prefetch = Prefetch(
            "presupuestos",
            queryset=Presupuesto.objects.order_by("-fecha_creacion"),
            to_attr="presupuestos_ordenados",
        )
        return queryset.annotate(
            presupuestos_count=Count("presupuestos", distinct=True),
            ultimo_presupuesto_fecha=Max("presupuestos__fecha_creacion"),
        ).prefetch_related(presupuestos_prefetch)

    @admin.display(description="Presupuestos", ordering="presupuestos_count")
    def presupuestos_count(self, obj):
        return obj.presupuestos_count

    @admin.display(description="Último presupuesto", ordering="ultimo_presupuesto_fecha")
    def ultimo_presupuesto_fecha(self, obj):
        return obj.ultimo_presupuesto_fecha or "—"

    @admin.display(description="Estado último presupuesto")
    def ultimo_presupuesto_estado(self, obj):
        ultimo = self._get_ultimo_presupuesto(obj)
        return ultimo.get_estado_display() if ultimo else "—"

    @admin.display(description="Abrir último presupuesto")
    def link_ultimo_presupuesto(self, obj):
        ultimo = self._get_ultimo_presupuesto(obj)
        if not ultimo:
            return "—"
        url = reverse("admin:reparaciones_presupuesto_change", args=[ultimo.pk])
        return format_html('<a href="{}">Abrir</a>', url)

    def _get_ultimo_presupuesto(self, obj):
        presupuestos = getattr(obj, "presupuestos_ordenados", None)
        if presupuestos:
            return presupuestos[0]
        return None

    @admin.display(description="Presupuesto")
    def presupuesto_resumen(self, obj):
        ultimo = self._get_ultimo_presupuesto(obj)
        if not ultimo:
            return "Sin presupuesto"
        estado = ultimo.get_estado_display() if hasattr(ultimo, "get_estado_display") else ultimo.estado
        resumen = estado
        if ultimo.monto is not None:
            resumen = f"{resumen} · {ultimo.moneda} {localize(ultimo.monto)}"
        url = reverse("admin:reparaciones_presupuesto_change", args=[ultimo.pk])
        return format_html('{} · <a href="{}">#{}</a>', resumen, url, ultimo.pk)
    def tiene_video(self, obj):
        return bool(obj.video)
    tiene_video.boolean = True
    tiene_video.short_description = "Video"

    fieldsets = (
        (None, {
            'fields': ('usuario', 'nombre_cliente', 'telefono', 'ubicacion', 'tipo_equipo', 'descripcion', 'imagen', 'estado', 'fecha_estimada_entrega', 'tiene_video')
        }),
    )

    actions = [
    'marcar_recibida',
    'marcar_pendiente_presupuesto',
    'marcar_pendiente_pago',
    'marcar_en_proceso',
    'marcar_listo_para_entregar',
    'marcar_entregado',
    'marcar_finalizado',
]


    # Definición de acciones
    def marcar_recibida(self, request, queryset):
        queryset.update(estado='recibida')
    marcar_recibida.short_description = "Marcar como: Recibimos tu solicitud"

    def marcar_pendiente_presupuesto(self, request, queryset):
        queryset.update(estado='pendiente_presupuesto')
    marcar_pendiente_presupuesto.short_description = "Marcar como: Estamos presupuestando el pedido"

    def marcar_pendiente_pago(self, request, queryset):
        queryset.update(estado='pendiente_pago')
    marcar_pendiente_pago.short_description = "Marcar como: A espera de aprobación y pago de seña"

    def marcar_en_proceso(self, request, queryset):
        queryset.update(estado='en_proceso')
    marcar_en_proceso.short_description = "Marcar como: En proceso de reparación"

    def marcar_listo_para_entregar(self, request, queryset):
        queryset.update(estado='listo_para_entregar')
    marcar_listo_para_entregar.short_description = "Marcar como: Listo para entregar"

    def marcar_entregado(self, request, queryset):
        queryset.update(estado='entregado')
    marcar_entregado.short_description = "Marcar como: Recibido por el cliente"

    def marcar_finalizado(self, request, queryset):
        queryset.update(estado='finalizado')
    marcar_finalizado.short_description = "Marcar como: Recibimos el pago final"

    def imagen_link(self, obj):
        if obj.imagen:
            return format_html(
                '<a href="{}" target="_blank">📷 Ver imagen</a>',
                obj.imagen.url
            )
        return "—"

    imagen_link.short_description = "Imagen"


    def video_link(self, obj):
        if obj.video:
            return format_html(
                '<a href="{}" target="_blank">🎬 Ver video</a>',
                obj.video.url
            )
        return "—"

    video_link.short_description = "Video"


@admin.register(Presupuesto)
class PresupuestoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reparacion",
        "usuario",
        "estado",
        "monto",
        "moneda",
        "fecha_creacion",
        "fecha_envio",
        "archivo_link",
        "notas_internas",
    )
    fields = (
        "reparacion",
        "usuario",
        "estado",
        "monto",
        "moneda",
        "archivo_presupuesto",
        "fecha_envio",
        "notas_internas",
    )
    list_filter = ("estado", "fecha_creacion", "reparacion", "usuario")
    search_fields = ("reparacion__id", "usuario__username", "usuario__email")
    ordering = ("-fecha_creacion",)
    readonly_fields = ("fecha_creacion",)
    actions = [
        "marcar_enviado",
        "marcar_aprobado",
        "marcar_rechazado",
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.estado == "enviado":
            Reparacion.objects.filter(pk=obj.reparacion_id).update(
                estado="pendiente_pago"
            )

    @admin.action(description="Marcar como: Enviado (Reparación a pendiente de pago)")
    def marcar_enviado(self, request, queryset):
        self._actualizar_estado(
            queryset,
            estado_presupuesto="enviado",
            estado_reparacion="pendiente_pago",
        )

    @admin.action(description="Marcar como: Aprobado (Reparación a en proceso)")
    def marcar_aprobado(self, request, queryset):
        self._actualizar_estado(
            queryset,
            estado_presupuesto="aprobado",
            estado_reparacion="en_proceso",
        )

    @admin.action(description="Marcar como: Rechazado")
    def marcar_rechazado(self, request, queryset):
        self._actualizar_estado(
            queryset,
            estado_presupuesto="rechazado",
            estado_reparacion=None,
        )

    def _actualizar_estado(self, queryset, estado_presupuesto, estado_reparacion):
        with transaction.atomic():
            queryset.update(estado=estado_presupuesto)
            if estado_reparacion:
                Reparacion.objects.filter(presupuestos__in=queryset).distinct().update(
                    estado=estado_reparacion
                )

    def archivo_link(self, obj):
        if obj.archivo_presupuesto:
            return format_html(
                '<a href="{}" target="_blank">📄 Ver presupuesto</a>',
                obj.archivo_presupuesto.url
            )
        return "—"

    archivo_link.short_description = "Archivo"
