def is_login(request):
    return bool(request.session.get("user_id"))


def is_admin(request):
    return request.session.get("role") == "admin"
