# -*- coding: utf-8 -*-

from django import template
from django.conf import settings
from datetime import time
from protocoller.miner import models

register = template.Library()


_result_map = dict(models.RESULT_TYPES)

@register.simple_tag
def print_pos(result):

    return _result_map.get(result.pos, result.pos) or ""


@register.simple_tag
def print_grp_pos(result):
    return _result_map.get(result.pos,
                           _result_map.get(result.pos_in_grp,
                                           result.pos_in_grp)) or ""


@register.simple_tag
def print_time(result):

    if _result_map.has_key(result.pos):
        return "N/A"

    if result.time.hour:
        return result.time.strftime('%H:%M:%S')
    else:
        return result.time.strftime('%M:%S')


@register.simple_tag
def time_diff(t1, t2):

    s1 = t1.hour*60*60 + t1.minute*60 + t1.second
    s2 = t2.hour*60*60 + t2.minute*60 + t2.second
    
    ds = s1-s2

    if ds <= 0:
        return ""
    
    (min, sec) = divmod(ds, 60)
    (hour, min) = divmod(min, 60)

    td = time(hour=hour, minute=min, second=sec)

    
    if td.hour:
        return td.strftime('+%H:%M:%S')
    elif td.minute:
        return td.strftime('+%M:%S')
    else:
        return td.strftime('+%M:%S')


@register.simple_tag
def time_diff2(t1, t2):

    s1 = t1.hour*60*60 + t1.minute*60 + t1.second
    s2 = t2.hour*60*60 + t2.minute*60 + t2.second
    
    ds = s1-s2

    if ds <= 0:
        return ""
    
    (min, sec) = divmod(ds, 60)
    (hour, min) = divmod(min, 60)

    td = time(hour=hour, minute=min, second=sec)

    if s2 != 0:
        return " %.3f"%(float(s1)/float(s2))
    else:
        return ""



# list of pairs (keyword, iconname)
PROVIDER_INFO = (('ya.ru', 'yandex.ico.gif'),
                 ('google.com', 'google.ico.gif'),
                 ('rambler', 'rambler.ico.gif'),
                 ('livejournal', 'livejournal.ico.gif'),
                 ('flickr', 'flickr.ico.gif'),
                 ('blogger', 'blogger.ico.gif'),
                 )


@register.simple_tag
def print_user(user):
    """Красиво форматирует имя пользователя в зависимости от типа учетной записи
    добавляет иконку соответствующего провайдера
    """
    def is_openid_user(user):
        return hasattr(user, 'openid_profiles') and \
            len(user.openid_profiles.all()) > 0

    def get_user_icon(user):
        openid_key = user.openid_profiles.all()[0].openid_key
        for key, icon in PROVIDER_INFO:
            if openid_key.find(key) != -1:
                return icon
        return 'openid.ico.gif'

    if is_openid_user(user):
        return """
<div class="profile">
<span class="profile-image">
<img src="%(media_url)simg/fi/%(icon_path)s" />
</span>
<span class="profile-name"> %(username)s </span>
</div>
""" % dict(media_url = settings.MEDIA_URL,
           icon_path = get_user_icon(user),
           username = user.openid_profiles.all()[0].nickname)
    else:
        return """
<div class="profile">
<span class="profile-name"> %(username)s </span>
</div>
""" % dict(username = user.username)

   

@register.simple_tag
def active(request, pattern):
    """Highlight active menu item in toolbar"""
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''
    
    





