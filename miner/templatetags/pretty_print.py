# -*- coding: utf-8 -*-

from django import template
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

    if s2 != 0:
        rel_td = " %.3f"%(float(s1)/float(s2))
    else:
        rel_td = ""

    if td.hour:
        return td.strftime('+%H:%M:%S')+rel_td
    elif td.minute:
        return td.strftime('+%M:%S')+rel_td
    else:
        return td.strftime('+%M:%S')+rel_td



