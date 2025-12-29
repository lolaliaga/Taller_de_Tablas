from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_reparacion, name='crear_reparacion'),
    path('registrar/', views.registrar, name='registrar'),
    path('staff/reparaciones/', views.staff_reparaciones, name='staff_reparaciones'),
    path(
        'staff/reparaciones/<int:reparacion_id>/',
        views.staff_reparacion_detalle,
        name='staff_reparacion_detalle',
    ),
    path(
        'staff/reparaciones/<int:reparacion_id>/finalizar/',
        views.staff_finalizar_reparacion,
        name='staff_finalizar_reparacion',
    ),
    path(
        'staff/reparaciones/<int:reparacion_id>/presupuestos/',
        views.staff_presupuestos,
        name='staff_presupuestos',
    ),
    path(
        'staff/reparaciones/<int:reparacion_id>/presupuestos/cargar/',
        views.staff_cargar_presupuesto,
        name='staff_cargar_presupuesto',
    ),
    path(
        'staff/reparaciones/<int:reparacion_id>/factura-final/',
        views.staff_factura_final,
        name='staff_factura_final',
    ),
    path('staff/finalizados/', views.staff_finalizados, name='staff_finalizados'),
    path(
        'staff/reparaciones/<int:reparacion_id>/reabrir/',
        views.staff_reabrir_reparacion,
        name='staff_reabrir_reparacion',
    ),
    path(
        'presupuestos/<int:presupuesto_id>/descargar/',
        views.descargar_presupuesto,
        name='descargar_presupuesto',
    ),
    path(
        'reparaciones/<int:reparacion_id>/factura-final/descargar/',
        views.descargar_factura_final,
        name='descargar_factura_final',
    ),
]
