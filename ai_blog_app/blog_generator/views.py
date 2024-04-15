import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

from .helpers.generate_blog import (
    generate_blog_from_transcript,
    get_transcript,
    get_youtube_title,
)
from .models import BLogPost


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def user_login(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(
                request, "login.html", {"error_message": "Invalid credentials"}
            )
    return render(request, "login.html")


def user_signup(request: HttpRequest) -> HttpResponse:
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


@login_required
def user_logout(request: HttpRequest) -> HttpResponseRedirect:
    logout(request)
    return redirect("/")


@csrf_exempt
def generate_blog(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"error": "invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        youtube_link = data["link"]
    except (KeyError, json.JSONDecodeError):
        return JsonResponse({"error": "invalid data sent"}, status=400)

    title = get_youtube_title(youtube_link)

    transcription = get_transcript(youtube_link)
    if not transcription:
        return JsonResponse({"error": "Failed to get transcript"}, status=500)

    blog_content = generate_blog_from_transcript(transcription)
    if not blog_content:
        return JsonResponse({"error": "Failed to generate blog"}, status=500)

    blog_post = BLogPost.objects.create(
        user=request.user,
        title=title,
        link=youtube_link,
        content=blog_content,
    )
    blog_post.save()

    return JsonResponse({"content": blog_content})


def blog_list(request: HttpRequest) -> HttpResponse:
    blog_articles = BLogPost.objects.filter(user=request.user)
    return render(request, "all-blogs.html", {"blog_articles": blog_articles})


def blog_details(request: HttpRequest, id: int) -> HttpResponse:
    blog_article_detail = BLogPost.objects.get(id=id)
    if request.user != blog_article_detail.user:
        return redirect("/")

    return render(
        request, "blog-details.html", {"blog_article_detail": blog_article_detail}
    )
