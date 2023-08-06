from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import render
from logging import Logger, INFO

logger = Logger(name=__name__, level=INFO)

try:
    CREATE_ACCOUNT = bool(settings.MODSHIB_CREATE_ACCOUNT)
except AttributeError:
    CREATE_ACCOUNT = False

try:
    ACTIVATE_ACCOUNT = bool(settings.MODSHIB_ACTIVATE_ACCOUNT)
except AttributeError:
    ACTIVATE_ACCOUNT = False


def sso(request: HttpRequest) -> HttpResponse:
    # nothing to do here...
    if request.user.is_authenticated:
        logger.info(
            f"User already authenticated, redirecting to {settings.LOGIN_REDIRECT_URL}"
        )
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    # fetch EPPN from headers, injected by mod_shib
    eppn = request.META.get("HTTP_EPPN", None)
    if not eppn:
        return render(
            request,
            "registration/sso_fail.html",
            {"login_redirect": settings.LOGIN_URL},
        )

    # find account
    eppn = eppn.strip()
    user = User.objects.filter(username=eppn).first()
    if not user and CREATE_ACCOUNT:
        logger.info(f"user {eppn} not found, creating account")
        user = User.objects.create_user(eppn)
        user.is_active = False
        user.save()
    if not user:
        logger.info(f"user {eppn} not found, rejecting auth")
        return render(request, "registration/sso_no_account.html")
    if not user.is_active and ACTIVATE_ACCOUNT:
        logger.info(f"user {eppn} not active, activating")
        user.is_active = True
        user.save()
    if not user.is_active:
        logger.info(f"user {eppn} inactive, rejecting auth")
        return render(request, "registration/sso_no_account.html")
    if user and user.is_active:
        logger.info(f"active user {eppn} found, login")
        login(request, user)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
