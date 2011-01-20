# -*- coding: utf-8 -*-
import re
import itertools
import random
import datetime
import csv

from pytils import translit
from django.db.models import Q
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django import forms
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
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



def season(dt):
    """Возвращает начальный год сезона, которому принадлежит дата
    Например season('2010-03-14') = 2009
    За начало сезона примем 1 октября
    """
    if dt >= datetime.date(dt.year, 10, 1):
        return dt.year
    return dt.year -1


def eval_groupby(*args, **kwargs):
    return [(k, list(l)) for k, l in
            itertools.groupby(*args, **kwargs)]
    

def logout_view(request):
    logout(request)
    return redirect('main')

def login_view(request):
    form = AuthenticationForm()
    return render_to_response('openid_signin.html', 
                              locals(),
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
    
    competition = get_object_or_404(models.Competition, id = comp_id)

    if competition.rating == models.ABS_RATING:
        return protocol(request, comp_id)

    results = models.Result.objects.filter(
        competition=competition).order_by('group').select_related()

    rg = itertools.groupby(results, lambda x:x.group)
    
    rg = [(group, sorted(l, cmp = res_in_grp_cmp)) for group,l in rg]
    result_groups = [(group, l[0].time, l) for group, l in rg if l]


    return render_to_response('protocol_groups.html',
                              {'result_groups': result_groups,
                               'comp': competition,
                               'alternate': competition.rating == models.BOTH_RATING
                               },
                              context_instance=RequestContext(request))


def get_person_results(person):
    results = models.Result.objects.select_related().filter(
        person=person).order_by('-competition__event__date')

    rg = itertools.groupby(
        results, lambda r:date2season(r.competition.event.date))

    rg = [(n,list(l)) for n,l in rg]
    return rg


def persons_view(request, year = None, month = None):
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(models.Person.objects.all().order_by(
            'surname', 'name', 'year'), 40)
    try:
        persons = paginator.page(page)
    except (EmptyPage, InvalidPage):
        persons = paginator.page(paginator.num_pages)

    return render_to_response('persons.html', locals(),
                              context_instance = RequestContext(request))


def person_view(request, person_id):
    person = get_object_or_404(models.Person, id = person_id)
    res_groups = get_person_results(person)
    return render_to_response('person.html', locals(),
                              context_instance=RequestContext(request))

def places_view(request):
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    paginator = Paginator(models.Place.objects.all().order_by('name'), 20)

    try:
        places = paginator.page(page)
    except (EmptyPage, InvalidPage):
        places = paginator.page(paginator.num_pages)

    return render_to_response('places.html', locals(),
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
        fields = ('name', 'link', 'description', 'location')
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
            place = form.save()
            if new_object:                
                place.created_by = request.user
                place.save()
            
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
    

def search_view(request):
    query = request.GET.get('query', '')
    paginator = Paginator(search_persons(query), 15)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        persons = paginator.page(page)
    except (EmptyPage, InvalidPage):
        persons = paginator.page(paginator.num_pages)


    cid_list = map(int, filter(None, request.GET.get('cl', '').split(',')))

    compare_list = list(models.Person.objects.filter(id__in=cid_list))
    cl = ','.join([str(c.id) for c in compare_list])

    for p in persons.object_list:
        p.is_in_list = p in compare_list
    
    return render_to_response('search_result.html', locals(),
                              context_instance=RequestContext(request))

    
def compare_view(request):
    def cmp_res(r1, r2):
        if r1.time and r2.time:
            return r1.time > r2.time
        if r1.pos > 0 or r2.pos > 0:
            return r1.pos < r2.pos
        return r1.pos_in_grp < r2.pos_in_grp
    
    cid_list = map(int, filter(None, request.GET.get('cl', '').split(',')))
    persons = list(models.Person.objects.filter(id__in=cid_list))

    results = models.Result.objects.select_related().filter(
        person__in = persons).order_by('-competition__event__date', 'competition')

    season_groups = []
    for season, results in eval_groupby(results, 
                                        lambda r: date2season(r.competition.event.date)):
        comp_res_groups = filter(
            lambda c: len(c[1])>1,
            eval_groupby(results, lambda x:x.competition))
        if not comp_res_groups:
            continue
        comp_res_groups = [(c, sorted(rl, cmp_res)) 
                           for c, rl in comp_res_groups]
        season_groups.append(
            (season,
             [(comp, results[0].time, results) for comp, results in comp_res_groups]
             ))

    return render_to_response('compare_results.html', locals(),
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

def past_events_view(request):
    try:
        page = int(request.GET.get('page', '1'))
        per_page = int(request.GET.get('per_page', '10'))
    except ValueError:
        page, per_page = 1, 10
    print request.GET, page, per_page
    today = datetime.date.today()
    objects = models.SportEvent.objects.filter(
        Q(date__lt = today, end_date = None)|
        Q(end_date__lt = today)).order_by('-date')
    paginator = Paginator(objects, per_page)
    try:
        events = paginator.page(page)
    except (EmptyPage, InvalidPage):
        events = paginator.page(paginator.num_pages)

    events_groups = [(year, eval_groupby(comps, lambda o:o.date))
                     for year, comps in eval_groupby(events.object_list, 
                                                     lambda o: o.date.year)]    
    
    return render_to_response('past_events.html', 
                              locals(),
                              context_instance = RequestContext(request))




def future_events_view(request):
    try:
        page = int(request.GET.get('page', '1'))
        per_page = int(request.GET.get('per_page', '10'))
    except ValueError:
        page, per_page = 1, 10
    today = datetime.date.today()
    objects = models.SportEvent.objects.filter(
        Q(date__gte = today, end_date = None)|
        Q(end_date__gte = today)).order_by('date')
    paginator = Paginator(objects, per_page)
    try:
        events = paginator.page(page)
    except (EmptyPage, InvalidPage):
        events = paginator.page(paginator.num_pages)
    events_groups = [(year, eval_groupby(comps, lambda o:o.date))
                     for year, comps in eval_groupby(events.object_list, 
                                                     lambda o: o.date.year)]    
    return render_to_response('future_events.html', 
                              locals(),
                              context_instance = RequestContext(request))



class SportEventForm(forms.ModelForm):
    date = forms.DateField(
        label = 'Дата',
        input_formats = ('%d.%m.%Y',),
        widget = forms.DateInput(format = '%d.%m.%Y'))
    place = forms.ModelChoiceField(
        queryset = models.Place.objects.all().order_by('name'),
        label = 'Место проведения')

    class Meta:
        model = models.SportEvent
        fields = ('place', 'date', 'name', 'registration_open',
                  'description', 'protocol_file')
        widgets = dict(
            description = MarkItUpWidget(),
            )

    class Media:
        js = ('js/jquery.ui.datepicker-ru.js', 
              "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/jquery-ui.min.js",
              "js/jquery.formset.min.js")
        
        css = dict(
            all = ("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.7/themes/redmond/jquery-ui.css",)
        )
    


@login_required
def edit_event_view(request, event_id = None):
    def custom_field_callback(field):
        if field.name in ('distance', 'start_time'):
            return field.formfield(
                widget = forms.TextInput(attrs = {'class': 'short-field'}))
        else:
            return field.formfield()

    if event_id:
        new_object = False
        event = get_object_or_404(models.SportEvent, id = event_id)
    else:
        new_object = True
        event = models.SportEvent()
        
    CompFormset = inlineformset_factory(
        models.SportEvent, models.Competition,
        fields = ('sex', 'name', 'style', 'start_type', 'distance',
                  'start_time'),
        formfield_callback = custom_field_callback,
        can_delete = True, extra = 1)

    if request.method == 'POST': 
        form = SportEventForm(request.POST, request.FILES, instance = event) 
        comp_formset = CompFormset(request.POST, request.FILES,
            instance = event)
        if form.is_valid() and comp_formset.is_valid():
            if new_object:
                event = form.save(commit = False)
                event.created_by = request.user
                event.save()
            else:
                form.save()
            comp_formset.save()
            return redirect(event)
    else:
        comp_formset = CompFormset(instance = event)
        form = SportEventForm(instance = event)

    return render_to_response('add_sport_event.html',
                              locals(),
                              context_instance = RequestContext(request))


def event_view(request, event_id):
    event = get_object_or_404(models.SportEvent, id = event_id)
    regs_count = models.RegistrationMembership.objects.filter(
        sport_event = event).count()
    return render_to_response('sport_event.html',
                              locals(), 
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
                reg_info = form.save(commit = False)
                reg_info.by_user = request.user
                reg_info.save()
                reg_mem = models.RegistrationMembership(info = reg_info,
                                                        sport_event = event)
                reg_mem.save()
                form = EventRegistrationForm()
        else:
            form = EventRegistrationForm()
        avail_regs = models.RegistrationInfo.objects.filter(
            by_user = request.user).exclude(sport_event = event)
        
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
    return register_on_event_view(request, event_id)
    

@login_required
def unsubscribe_from_event_view(request, event_id, reg_id):
    reg_info = get_object_or_404(models.RegistrationInfo, id = reg_id,
                                 by_user = request.user)
    event = get_object_or_404(models.SportEvent, id = event_id)
    for m in models.RegistrationMembership.objects.filter(
        info = reg_info, sport_event = event):
        m.delete()
    
    return register_on_event_view(request, event_id)


def get_reg_info_view(request, event_id):
    event = get_object_or_404(models.SportEvent, id = event_id)
    reg_info = models.RegistrationMembership.objects.filter(
        sport_event = event).order_by(
        'info__surname', 'info__name').select_related()
    response = HttpResponse(mimetype='text/csv')
    filename = translit.slugify(event.name) + '_' + str(event.date.year)
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % filename

    writer = csv.writer(response)
    writer.writerow(['№', 'Фамилия Имя', 'Пол', 'Год', 'Звание', 'Город', 'Клуб'])
    sex_dict = dict(models.SEX_TYPES)
    rank_dict = dict(models.RANK_TYPES)

    for i, mem in enumerate(reg_info, 1):
        info = mem.info
        writer.writerow(
            map(lambda s: s.encode('utf-8'),
                [str(i), info.surname + ' ' + info.name, sex_dict[info.sex],
                 str(info.year), rank_dict[info.rank], info.city, 
                 info.club]))
    return response


def main_view(request):
    today = datetime.date.today()
    per_page = 10
    coming_events = models.SportEvent.objects.filter(
        Q(date__gte = today, end_date = None)|
        Q(end_date__gte = today)).order_by('date')

    past_events = models.SportEvent.objects.filter(
        Q(date__lt = today, end_date = None)|
        Q(end_date__lt = today)).order_by('-date')

    coming_page, past_page = \
        [Paginator(l, per_page).page(1) for l in (coming_events, past_events)]

    coming_groups = [(year, eval_groupby(comps, lambda o:o.date))
                     for year, comps in eval_groupby(coming_page.object_list, 
                                                     lambda o: o.date.year)]
    past_groups = [(year, eval_groupby(comps, lambda o:o.date))
                     for year, comps in eval_groupby(past_page.object_list, 
                                                     lambda o: o.date.year)]    
            
    return render_to_response('main.html', locals(),
                              context_instance = RequestContext(request))
