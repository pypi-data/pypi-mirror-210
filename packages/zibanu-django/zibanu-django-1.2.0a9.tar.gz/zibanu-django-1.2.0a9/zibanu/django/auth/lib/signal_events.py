# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/05/23 12:02
# Project:      Zibanu - Django
# Module Name:  signal_events
# Description:
# ****************************************************************
from django.apps import apps
from django.dispatch import receiver
from typing import Any
from zibanu.django.auth.lib.signals import *
from zibanu.django.utils import get_ip_address

def save_on_logging(**kwargs):
    """
    Method to save on LOG model of loggin app
    :param kwargs:
    :return: None
    """
    if apps.is_installed("zibanu.django.logging"):
        from zibanu.django.logging.models import Log
        log = Log(**kwargs)
        log.save()

@receiver(change_password)
@receiver(request_password)
def auth_generic_event(sender: Any, user: Any, **kwargs) -> None:
    """
    Generic event for change or request password
    :param sender: sender class
    :param user: user object
    :param kwargs: kwargs dict
    :return:
    """
    class_name = sender.__name__
    ip_address = get_ip_address(kwargs.get("request", None))
    action = "probe"
    if apps.is_installed("zibanu.django.logging"):
        from zibanu.django.logging.models import Log
        log = Log(user=user, sender=class_name, action=action, ip_address=ip_address)
        log.save()

