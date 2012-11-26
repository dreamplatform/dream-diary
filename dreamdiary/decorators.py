
#encoding=utf-8

from django.http import HttpRequest
from django.shortcuts import render

def supervisor_required(func):
    """
    Decorator to check if user is supervisor, use with 'login_required' decorator.
    """
    def wrapper(*args, **kwargs):
        if len(args) and isinstance(args[0], HttpRequest):
            if args[0].user.has_perm(u'dreamdiary.supervisor'):
                return func(*args, **kwargs)
            return render(args[0], 'dreamdiary/needed_permissions.html')
        else:
            raise AttributeError(u'supervisor_required decorator requires HttpRequest as argument')
    return wrapper

def user_required(func):
    """
    Decorator to check if user is user, use with 'login_required' decorator.
    """
    def wrapper(*args, **kwargs):
        if len(args) and isinstance(args[0], HttpRequest):
            if args[0].user.has_perm(u'dreamdiary.user'):
                return func(*args, **kwargs)
            return render(args[0], 'dreamdiary/needed_permissions.html')
        else:
            raise AttributeError(u'user_required decorator requires HttpRequest as argument')
    return wrapper

def supervisor_or_user_required(func):
    """
    Decorator to check if user is supervisor or user, use with 'login_required' decorator.
    """
    def wrapper(*args, **kwargs):
        if len(args) and isinstance(args[0], HttpRequest):
            is_supervisor = args[0].user.has_perm(u'dreamdiary.supervisor')
            is_user = args[0].user.has_perm(u'dreamdiary.user')
            if is_supervisor or is_user:
                return func(*args, **kwargs)
            return render(args[0], 'dreamdiary/needed_permissions.html')
        else:
            raise AttributeError(u'supervisor_or_user_required decorator requires HttpRequest as argument')
    return wrapper

