from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render


# Create your views here.
def index(request) -> None:
    return render(request, "index.html")


def user_login(request) -> None:
    return render(request, "login.html")


def user_signup(request) -> None:
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation_password = request.POST["confirmation-password"]

        if password != confirmation_password:
            return render(
                request, "signup.html", {"error_message": "Password don't match"}
            )
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            login(request, user)
            return redirect("/")
        except:
            return render(
                request, "signup.html", {"error_message": "Error creating user"}
            )

    return render(request, "signup.html")


def user_logout(request) -> None:
    pass
