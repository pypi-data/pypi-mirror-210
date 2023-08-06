# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/05/23 10:23
# Project:      Zibanu - Django
# Module Name:  utils
# Description:  Utils tools for auth module
# ****************************************************************
from django.contrib import auth
from rest_framework_simplejwt.models import TokenUser
from typing import Any


def get_user(user: Any) -> Any:
    """
    Function to get User objecto from TokenUser or another object.
    :param user: Any: User object to be converted
    :return: User: User object.
    """
    local_user = user
    user_model = auth.get_user_model()
    if isinstance(user, TokenUser):
        local_user = user_model.objects.get(pk=local_user.id)

    return local_user


def get_user_object(user: Any) -> Any:
    """
    Legacy function. This function will be discontinued in future versions.
    :param user: Any: User object from request or auth to be returned
    :return: User: User object
    """
    return get_user(user)