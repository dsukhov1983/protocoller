# coding: utf-8
from django.shortcuts import get_object_or_404
from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register

from . import common
from . import models
from .templatetags.pretty_print import person_compare_row


@dajaxice_register
def add_to_compare(request, person_id):
    person_id = int(person_id)
    person = get_object_or_404(models.Person, id=person_id)
    compare_set = request.session.get(common.COMPARE_LIST_SESSION_KEY, set())
    dajax = Dajax()
    if person_id not in compare_set:
        compare_set.add(person_id)
        request.session[common.COMPARE_LIST_SESSION_KEY] = compare_set
        dajax.append("#compare-list-body", "innerHTML", person_compare_row(person))
        dajax.add_css_class("#add-to-compare-person-%s-button" % person_id, "hide")
        dajax.remove_css_class("#compare-persons-block", "hide")
    return dajax.json()


@dajaxice_register
def remove_from_compare(request, person_id):
    person_id = int(person_id)
    compare_set = request.session.get(common.COMPARE_LIST_SESSION_KEY, set())
    dajax = Dajax()
    if person_id in compare_set:
        compare_set.remove(person_id)
        request.session[common.COMPARE_LIST_SESSION_KEY] = compare_set
        dajax.remove('#compare-person-%s' % person_id)
        dajax.remove_css_class("#add-to-compare-person-%s-button" % person_id, "hide")
    return dajax.json()

