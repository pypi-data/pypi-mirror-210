# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/05/23 11:59
# Project:      Zibanu - Django
# Module Name:  signals
# Description:
# ****************************************************************
from django import dispatch

change_password = dispatch.Signal()
request_password = dispatch.Signal()
