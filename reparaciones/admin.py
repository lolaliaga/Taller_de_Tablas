from django.contrib import admin
from .models import Reparacion

@admin.register(Reparacion)
class ReparacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'telefono', 'ubicacion', 'tipo_equipo', 'estado', 'fecha_finalizacion', 'usuario')
    list_filter = ('estado', 'tipo_equipo', 'usuario')
    search_fields = ('nombre_cliente', 'telefono', 'ubicacion', 'tipo_equipo')
    ordering = ('-id',)
    readonly_fields = ('usuario',)  # El usuario que creó la reparación no se puede modificar desde el admin

    fieldsets = (
        (None, {
            'fields': ('usuario', 'nombre_cliente', 'telefono', 'ubicacion', 'tipo_equipo', 'descripcion', 'imagen', 'estado', 'fecha_finalizacion')
        }),
    )

    actions = [
        'marcar_pendiente_presupuesto',
        'marcar_pendiente_pago',
        'marcar_en_proceso',
        'marcar_listo_para_entregar',
        'marcar_entregado',
        'marcar_finalizado',
    ]

    # Definición de acciones
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
