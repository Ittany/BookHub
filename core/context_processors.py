def role_context(request):
    user = request.user
    staff = bool(user.is_authenticated and (user.is_superuser or user.is_staff or (hasattr(user, 'perfil') and user.perfil.rol == 'bibliotecario')))
    return {'es_personal': staff}
