from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import RegistroForm, ReparacionForm
from .models import Reparacion
from django.contrib.auth.views import LoginView

# -----------------------------
# Registro de usuario
# -----------------------------
def registrar(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'reparaciones/registrar.html', {'form': form})


# -----------------------------
# Crear reparación
# -----------------------------
@login_required
def crear_reparacion(request):
    if request.method == 'POST':
        form = ReparacionForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            reparacion = form.save(commit=False)
            reparacion.usuario = request.user
            reparacion.save()
            return redirect('inicio')
    else:
        form = ReparacionForm(user=request.user)

    return render(request, 'reparaciones/crear_reparacion.html', {'form': form})


# -----------------------------
# Dashboard de usuario
# -----------------------------
@login_required
def inicio(request):
    reparaciones = Reparacion.objects.filter(
        usuario=request.user
    ).order_by('orden_usuario', '-created_at')

    return render(
        request,
        'reparaciones/inicio.html',
        {'reparaciones': reparaciones}
    )


# -----------------------------
# Login personalizado con "Remember me"
# -----------------------------
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        remember_me = self.request.POST.get('remember_me')
        if not remember_me:
            # La sesión expira al cerrar el navegador
            self.request.session.set_expiry(0)
        else:
            # Usa la duración por defecto de SESSION_COOKIE_AGE
            self.request.session.set_expiry(None)
        return super().form_valid(form)
