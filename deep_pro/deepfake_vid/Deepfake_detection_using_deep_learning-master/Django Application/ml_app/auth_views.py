from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()
AUTH_TEMPLATE = "auth.html"


def register_view(request):
    if request.user.is_authenticated:
        return redirect("ml_app:home")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        errors = {}

        if not name:
            errors["name"] = "Name is required."
        elif len(name) < 2:
            errors["name"] = "Name must be at least 2 characters."

        if not email:
            errors["email"] = "Email is required."
        elif "@" not in email:
            errors["email"] = "Enter a valid email address."
        elif User.objects.filter(email__iexact=email).exists():
            errors["email"] = "An account with this email already exists."

        if not password:
            errors["password"] = "Password is required."
        elif len(password) < 6:
            errors["password"] = "Password must be at least 6 characters."

        if password and confirm_password != password:
            errors["confirm_password"] = "Passwords do not match."

        if name and User.objects.filter(username__iexact=name).exists():
            errors["name"] = "This name is already taken."

        if errors:
            return render(request, AUTH_TEMPLATE, {
                "tab": "register",
                "errors": errors,
                "form_data": {"name": name, "email": email},
            })

        user = User.objects.create_user(
            username=name,
            email=email,
            password=password,
            first_name=name,
        )
        login(request, user, backend="ml_app.auth_backend.EmailOrNameBackend")
        messages.success(request, f"Welcome to DeepShield AI, {name}!")
        return redirect("ml_app:home")

    return render(request, AUTH_TEMPLATE, {"tab": "register"})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("ml_app:home")

    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")

        if not identifier:
            return render(request, AUTH_TEMPLATE, {
                "tab": "login",
                "errors": {"identifier": "Email or name is required."},
                "form_data": {"identifier": identifier},
            })
        if not password:
            return render(request, AUTH_TEMPLATE, {
                "tab": "login",
                "errors": {"password": "Password is required."},
                "form_data": {"identifier": identifier},
            })

        user = authenticate(request, identifier=identifier, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            return render(request, AUTH_TEMPLATE, {
                "tab": "login",
                "errors": {"general": "Invalid credentials. Check your email/name and password."},
                "form_data": {"identifier": identifier},
            })

    return render(request, AUTH_TEMPLATE, {"tab": "login"})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("ml_app:login")
