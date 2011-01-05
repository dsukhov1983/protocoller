# -*- coding: utf-8 -*-
import re
import itertools
import operator
import random
import datetime

from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from markitup.widgets import MarkItUpWidget
from protocoller.miner import models


SAMPLE_SEARCHES=(u'Ильин Василий',
                 u'Барышников Алексей',
                 u'Климов Михаил',
                 u'Кукрус Андрей',
                 u'Зарицкий Михаил',
                 u'Малыгин Александр',
                 u'Кочетков Олег',
                 u'Сухов Дмитрий',
                 u'Кудиенко Михаил',
                 u'Исаев Иван',
                 u'Краснов Андрей',
                 u'Арих Андрей',
                 u'Нестеров Анатолий',
                 u'Хачкованян Карен',
                 u'Долгополов Никита')

def logout_view(request):
    logout(request)
    return redirect('comp_list_view')

def login_view(request):
    return render_to_response('openid_signin.html', 
                              context_instance=RequestContext(request))


def get_random_search():
    return SAMPLE_SEARCHES[random.randint(0,
                                          len(SAMPLE_SEARCHES)-1)]

def date2season(dt):
    """converts datetime to season like 2008/2009"""
    y = dt.year
    if dt.month <= 6:
        return "%s/%s"%(y-1, y)
    else:
        return "%s/%s"%(y, y+1)
    


def about(request):
    return render_to_response('about.html',
                              context_instance=RequestContext(request))



def protocol(request, comp_id):
    competition = get_object_or_404(models.Competition,
                                    id = comp_id)

    if competition.rating == models.GROUP_RATING:
        return redirect('protocol_by_groups', comp_id=comp_id)
    
    results = models.Result.objects.select_related().filter(competition=competition)

    ores = results.filter(pos__gt=0).order_by('pos')
    other_res = results.filter(pos__lte=0).order_by('pos')
    results = list(ores) + list(other_res)


    return render_to_response('protocol.html',
                              {'results': results,
                               'comp': competition,
                               'alternate': competition.rating == models.BOTH_RATING
                               },
                              context_instance=RequestContext(request))

def protocol_by_groups(request, comp_id):

    def res_in_grp_cmp(r1, r2):
        r1, r2 = r1.pos_in_grp, r2.pos_in_grp
        if r1 > 0 and r2 > 0:
            if r1 > r2:
                return 1
            elif r1 == r2:
                return 0
            else:
                return -1
        elif r1 > 0:
            return -1
        elif r2 > 0:
            return 1
        else:
            return 0
    
    competition = get_object_or_404(models.Competition,
                                    id=comp_id)

    if competition.rating == models.ABS_RATING:
        return redirect('protocol', comp_id=comp_id)

    results = models.Result.objects.select_related().filter(competition=competition).order_by('group')

    rg = itertools.groupby(results,
                           lambda x:x.group)
    
    rg = [(n,sorted(l,cmp=res_in_grp_cmp)) for n,l in rg]


    return render_to_response('protocol_groups.html',
                              {'result_groups': rg,
                               'comp': competition,
                               'alternate': competition.rating == models.BOTH_RATING
                               },
                              context_instance=RequestContext(request))



def get_person_results(person):
    results = models.Result.objects.select_related().filter(person=person).order_by('-competition__event__date')

    rg = itertools.groupby(results,
                           lambda r:date2season(r.competition.event.date))

    rg = [(n,list(l)) for n,l in rg]
    return rg

def person_results(request, person_id):
    person = get_object_or_404(models.Person, id = person_id)
    rg = get_person_results(person)
    return render_to_response('summary_results.html',
                              {'res_groups': rg,
                               'person': person},
                              context_instance=RequestContext(request))

def places_view(request):
    try:
        page = int(request.GET.get('page', [1])[0])
    except ValueError:
        page = 1
    paginator = Paginator(models.Place.objects.all(), 20)

    # If page request (9999) is out of range, deliver last page of results.
    try:
        places = paginator.page(page)
    except (EmptyPage, InvalidPage):
        places = paginator.page(paginator.num_pages)

    return render_to_response('places.html', 
                              dict(places = places),
                              context_instance = RequestContext(request))



def get_place_or_404(id):
    try:
        return get_object_or_404(models.Place, id = int(id))
    except ValueError:
        return get_object_or_404(models.Place, slug = id)

def place_view(request, id = None):
    place = get_place_or_404(id)
    return render_to_response('place.html', dict(place = place),
                              context_instance = RequestContext(request))

class PlaceForm(forms.ModelForm):
    class Meta:
        model = models.Place
        widgets = {
            'description': MarkItUpWidget(),
            'location': forms.HiddenInput(),
            }

@login_required
def edit_place_view(request, id = None):
    new_object = False
    if id:
        place = get_place_or_404(id)
    else:
        new_object = True
        place = models.Place()

    if request.method == 'POST':
        form = PlaceForm(request.POST, instance = place) 
        if form.is_valid(): 
            if new_object:
                place = form.save(commit = False)
                place.created_by = request.user
                place.save()
            else:
                form.save()
            return redirect(place)
    else:
        form = PlaceForm(instance = place)
        
    return render_to_response('add_place.html',
                              locals(),
                              context_instance = RequestContext(request))
    

def search_persons(query):
    ql = map(lambda s:s.title(),
             filter(None, query.strip().split(' ')))

    if len(ql)>1:
        n, s = ql[:2]        
        persons = models.Person.objects.filter(
            (Q(name__icontains=n) & Q(surname__icontains=s))|
            (Q(name__icontains=s) & Q(surname__icontains=n)))
    elif len(ql) == 1:
        q = ql[0]
        persons = models.Person.objects.filter(
            (Q(name__icontains=q) | Q(surname__icontains=q)))
    else:
        persons = []    

    return persons
    

def search(request):
    q = request.GET.get('query', '')
    paginator = Paginator(search_persons(q), 15)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        persons = paginator.page(page)
    except (EmptyPage, InvalidPage):
        persons = paginator.page(paginator.num_pages)

    return render_to_response('search_result.html',
                              {'persons': persons,
                               'query': q,
                               'sample_search':get_random_search()},
                              context_instance=RequestContext(request))


def compare(request, add=None, delete=None):
    q = request.GET.get('query', '')
    paginator = Paginator(search_persons(q), 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1


    try:
        persons = paginator.page(page)
    except (EmptyPage, InvalidPage):
        persons = paginator.page(paginator.num_pages)


    csid_list = filter(None, request.GET.get('cl', '').split(','))
    cid_list = []

    for c in csid_list:
        try:
            cid_list.append(int(c))
        except:
            pass
                           

    compare_list = list(models.Person.objects.filter(id__in=cid_list))

    try:

        if add:
            p = get_object_or_404(models.Person,
                                  id=int(add))
            compare_list.append(p)

        if delete:
            p = get_object_or_404(models.Person,
                                  id=int(delete))
            compare_list.remove(p)
    except ValueError,e:
        ##TODO: log error
        print e

    cl = ','.join([str(c.id) for c in compare_list])

    for p in persons.object_list:
        p.is_in_list = p in compare_list

    return render_to_response('compare.html',
                              {'persons': persons,
                               'compare': compare_list,
                               'query': q,
                               'cl': cl,
                               'sample_search':get_random_search()},
                              context_instance=RequestContext(request))
    

def do_compare(request):
    
    csid_list = filter(None, request.GET.get('cl', '').split(','))
    cid_list = []

    for c in csid_list:
        try:
            cid_list.append(int(c))
        except:
            pass

    compare_list = list(models.Person.objects.filter(id__in=cid_list))

    
    results = models.Result.objects.select_related().filter(person__in=compare_list).order_by('-competition__event__date', 'competition')

    rgl = itertools.groupby(results,
                           lambda r:date2season(r.competition.event.date))

    rgl = [[n,list(l)] for n,l in rgl]

    for rg in rgl:
        rg[1] =  itertools.groupby(rg[1],
                                   lambda x:x.competition)
    
        rg[1] = filter(lambda c:len(c[1])>1,
                       [(c,list(l)) for c,l in rg[1]])

    rgl = filter(lambda e:len(e[1])>0,
                 rgl)

    return render_to_response('compare_results.html',
                              {'persons': compare_list,
                               'res_groups': rgl},
                              context_instance=RequestContext(request))



class PersonFeedbackForm(forms.ModelForm):

    person = forms.ModelChoiceField(queryset=models.Person.objects.all(),
                                    widget=forms.HiddenInput(),
                                    required=False)

    wrong_results = forms.ModelMultipleChoiceField(
        queryset=models.Result.objects.all(),
        widget=forms.HiddenInput(),
        required=False)
                                                   

    class Meta:
        model=models.PersonFeedback


def feedback_person(request, person):
    p = get_object_or_404(models.Person,
                          id=int(person))

    rg = get_person_results(p)
    
    if request.method != 'POST':
        init_val = dict((key, getattr(p, key)) for key in
                        ['name', 'surname', 'year', 'sex',
                         'rank', 'club', 'city'])
        init_val['person'] = p.id
        form = PersonFeedbackForm(initial=init_val)

        return render_to_response('person_feedback.html',
                                  {'person': p,
                                   'res_groups': rg,
                                   'form': form},
                                  context_instance=RequestContext(request))


    form = PersonFeedbackForm(request.POST)
    form.person = p

    rexp = re.compile('id_result_(\d+)_DELETE')        
    wrid_list = []    
    for key, val in request.POST.items():
        v = rexp.match(key)
        if v and val == 'on':
            wrid_list.append(int(v.group(1)))                               
            

    if form.is_valid():

        fb = form.save()
        for w in wrid_list:
            try:
                wr = models.Result.objects.get(id=w)
                fb.wrong_results.add(wr)
            except Exception,e:
                print e
        fb.save()
        
        return render_to_response('success_feedback.html',
                                  context_instance=RequestContext(request))
    
    else:
        for season, results in rg:
            for r in results:
                r.is_deleted = r.id in wrid_list

        return render_to_response('person_feedback.html',
                                  {'person': p,
                                   'res_groups': rg,
                                   'form': form},
                                  context_instance=RequestContext(request))



def get_event_summary():

    months = models.SportEvent.objects.extra(
        select={'month':'strftime("%%Y-%%m",date)'}
        ).order_by('-date').values_list('month')


    months = map(lambda s:datetime.datetime.strptime(s[0],'%Y-%m'), months)

    mc = [(m, len(list(l))) for m, l in itertools.groupby(months)]

    ys = itertools.groupby(mc,
                           lambda (d,c): d.year)

    return [(y, list(l)) for y,l in ys]
    


def comp_list_view(request, year = None, month = None):
    try:
        year = year and int(year)
        month = month and int(month)
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    comp_list = models.SportEvent.objects.all().select_related()\
                .order_by('-date')
    
    if year is not None:
        if month is not None:
            start_date = datetime.date(year, month, 1)
            if month == 12:
                end_date = datetime.date(year + 1, 1, 1)
            else:
                end_date = datetime.date(year, month+1, 1)
        else:
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year + 1, 1, 1)

        comp_list = comp_list.filter(date__gte = start_date,
                                     date__lt = end_date)

    paginator = Paginator(comp_list, 30)
    comp_list = paginator.page(page)
    date_groups = itertools.groupby(comp_list.object_list,
                                    lambda c:c.date)
    
    comp_groups = []
    for szn, dg in itertools.groupby(date_groups,
                                     lambda d:d[0].year):
        dg = [(d, list(l)) for d,l in dg]
        comp_groups.append((szn, dg))            
        
    return render_to_response('protocols.html',
                              {'comp_groups': comp_groups,
                               'cl_page': comp_list,
                               'sample_search':get_random_search(),
                               'event_summary': get_event_summary(),
                               'cur_year': year,
                               'cur_month': month},
                              context_instance = RequestContext(request))


def events_view(request, year = None, month = None):
    events = models.SportEvent.objects.filter(date__gte = datetime.datetime.now())\
        .select_related()
    return render_to_response('events.html',
                              dict(events = events),
                              context_instance = RequestContext(request))


class SportEventForm(forms.ModelForm):
    date = forms.DateField(input_formats = ('%d.%m.%Y',))

    class Meta:
        model = models.SportEvent
        fields = ('place', 'date', 'name',
                  'description')
        widgets = dict(
            date = forms.DateInput(format = '%d.%m.%Y'),
            description = MarkItUpWidget(),
            )

    class Media:
        js = ('js/jquery.ui.datepicker-ru.js', 
              "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/jquery-ui.min.js")
        
        css = dict(
            all = ("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/themes/redmond/jquery-ui.css",)
        )
    


@login_required
def edit_event_view(request, event_id = None):
    if event_id:
        new_object = False
        event = get_object_or_404(models.SportEvent, id = event_id)
    else:
        new_object = True
        event = models.SportEvent()

    if request.method == 'POST': 
        form = SportEventForm(request.POST, instance = event) 
        if form.is_valid():
            if new_object:
                event = form.save(commit = False)
                event.created_by = request.user
                event.save()
            else:
                form.save()
            return redirect(event)
    else:
        form = SportEventForm(instance = event)

    return render_to_response('add_sport_event.html',
                              locals(),
                              context_instance = RequestContext(request))


def event_view(request, event_id):
    event = get_object_or_404(models.SportEvent, id = event_id)
    return render_to_response('sport_event.html',
                              dict(event = event), 
                              context_instance = RequestContext(request))


class EventRegistrationForm(forms.ModelForm):
    class Meta:
        model = models.RegistrationInfo
        widgets = {
            'sport_event': forms.HiddenInput(),
            }

def register_on_event_view(request, event_id):
    event = get_object_or_404(models.SportEvent, id = event_id)
    
    form = None
    avail_regs, done_regs = [], []
    if request.user.is_authenticated():
        if request.method == 'POST':
            form = EventRegistrationForm(request.POST)
            if form.is_valid():
                reg_info = form.save()
                reg_mem = models.RegistrationMembership(info = reg_info,
                                                        sport_event = event)
                reg_mem.save()
                form = EventRegistrationForm()
        else:
            form = EventRegistrationForm()
        avail_regs = models.RegistrationInfo.objects.filter(
            by_user = request.user).exclude(sport_event = event)
        done_regs = models.RegistrationInfo.objects.filter(
            by_user = request.user,
            sport_event = event)
        
    reg_list = models.RegistrationInfo.objects.filter(sport_event = event)
    return render_to_response(
        'event_registration.html',
        locals(), 
        context_instance = RequestContext(request))
    

@login_required
def subscribe_on_event_view(request, event_id, reg_id):
    reg_info = get_object_or_404(models.RegistrationInfo, id = reg_id,
                                 by_user = request.user)
    event = get_object_or_404(models.SportEvent, id = event_id)
    
    mem = models.RegistrationMembership(info = reg_info,
                                        sport_event = event)
    mem.save()
    reg_list = models.RegistrationInfo.objects.filter(sport_event = event)
    avail_regs = models.RegistrationInfo.objects.filter(
        by_user = request.user).exclude(sport_event = event)
    done_regs = models.RegistrationInfo.objects.filter(
        by_user = request.user,
        sport_event = event)
    return render_to_response(
        'event_registration.html',
        locals(), 
        context_instance = RequestContext(request))
    

@login_required
def unsubscribe_from_event_view(request, event_id, reg_id):
    reg_info = get_object_or_404(models.RegistrationInfo, id = reg_id,
                                 by_user = request.user)
    event = get_object_or_404(models.SportEvent, id = event_id)
    
    mem = get_object_or_404(models.RegistrationMembership,
                            info = reg_info,
                            sport_event = event)
    mem.delete()
    reg_list = models.RegistrationInfo.objects.filter(sport_event = event)
    avail_regs = models.RegistrationInfo.objects.filter(
        by_user = request.user).exclude(sport_event = event)
    done_regs = models.RegistrationInfo.objects.filter(
        by_user = request.user,
        sport_event = event)
    return render_to_response(
        'event_registration.html',
        locals(), 
        context_instance = RequestContext(request))


def sportsmen_view(request, year = None, month = None):
    return render_to_response('sportsmen.html',
                              context_instance = RequestContext(request))
