# -*- coding: utf-8 -*-
import sys
import datetime
import itertools
import csv

from lxml import html

from protocoller.miner import models
from protocoller.miner import search_tree
from protocoller.miner.html_parser import ST


comparer = search_tree.SmartComparer()

RESULT_VARIANTS = (
    (models.DNS, [u'dns', u'не старт', u'неявка']),
    (models.DNF, [u'dnf', u'сош', u'не фин']),
    (models.DQF, [u'dqf', u'диск', u'рез. аннул.', u'снят'])
    )
        

def format_name(val):
    return val.capitalize()

def name_surname(obj, val, delimiter=' '):
    l = filter(None, val.strip().split(delimiter))
    obj.surname = l[0].capitalize()
    if len(l)>1:
        obj.name = l[1].capitalize()

def sex_parse(obj, val):
    val = val.strip().lower()
    if val in ('ж', 'жен'):
        obj.sex = models.FEMALE
    elif val in ('м', 'муж'):
        obj.sex = models.MALE
    else:
        obj.sex = models.UNKNOWN


def int_parse(val):
    try:
        return int(val)
    except:
        return 0


def str_parse(val):
    return unicode(val).strip().capitalize()


def result_parse(val):
    val = val.strip().lower()
    for (code, nl) in RESULT_VARIANTS:
        for n in nl:
            if val.find(n) == 0:
                return code
    try:
        return int(val)
    except:
        return 0


def time_parse(obj, val):
    val = val.strip().lower()
    rp = result_parse(val)
    if rp:
        obj.pos = rp
        obj.time = datetime.time()
        return

    for sep in (',', '.'):
        val = val.split(sep)[0]

    for fmt in ('%H:%M:%S', '%M:%S'):
        try:
            d = datetime.datetime.strptime(val, fmt)
            obj.time = datetime.time(d.hour, d.minute, d.second)
            return
        except:
            pass

    print "Failed to parse date %s"%val
    obj.time = datetime.time()


def rank_parse(val):
    val = val.strip().lower()
    for t, v in models.RANK_TYPES:
        if val == v:
            return t
    return models.NR


def parse_list(rlist, fields, defaults = {}):
    def raw2Result(rec, fields, defaults = {}):
        res = models.RawResult()
        for field, val in zip(fields, rec):
            _parse_map[field](res, val)
        for name, value in defaults.items():
            setattr(res, name, value)    
        return res

    return [raw2Result(r, fields, defaults) for r in rlist]

(POS, NUM, GROUP, POS_IN_GROUP, NAME, SURNAME, NAME_SURNAME,
 YEAR, SEX, RANK, CLUB, CITY, TIME, QUALIF_RANK, IGNORE) = range(15)

_parse_map = {
    POS: ST(result_parse, 'pos'),
    NUM: ST(int_parse,'number'),
    GROUP: ST(str_parse, 'group'),
    POS_IN_GROUP: ST(result_parse, 'pos_in_grp'),
    NAME: ST(str_parse, 'name'),
    SURNAME: ST(str_parse, 'surname'),
    NAME_SURNAME: name_surname,
    YEAR: ST(int_parse, 'year'),
    SEX: sex_parse,
    RANK: ST(rank_parse, 'rank'),
    QUALIF_RANK: ST(rank_parse, 'qualif_rank'),
    CLUB: ST(str_parse, 'club'),
    CITY: ST(str_parse, 'city'),
    TIME: time_parse,
    IGNORE: lambda obj, val: None}
    
equivalence_sets = (u'ао', u'её', u'оё', u'зс', u'гк', u'бп', u'ий', u'бп',
                    u'щш')

_equiv_map = {}
for s in equivalence_sets:
    for c in s:
        _equiv_map[c] = _equiv_map.get(c, []) + list(s)

def fuzy_equal(a, b):
    if a == b or \
       b in _equiv_map.get(a, []):
        return True
    return False

def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    a, b = a.lower(), b.lower()
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if not fuzy_equal(a[j-1], b[i-1]):
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]


def combinations(iter1, iter2):
    iter2 = tuple(iter2)
    for i in iter1:
        for j in iter2:
            yield (i,j)


def measure(a, b):
    res = 0
    res += 2*levenshtein(a.surname, b.surname)
    res += levenshtein(a.name or "", b.name or "")
    if a.year and b.year:
        res += levenshtein(str(a.year), str(b.year))
     
    return res

    
THRESHOLD = 4 #порог для поиска похожих Person
all_persons = list(models.Person.objects.all())

def find_best_result(comp):
    try:
        br = models.Result.objects.get(competition = comp, pos = 1)
        comp.best_result = br.time
        print br.time
        comp.save()
        return
    except Exception,e:
        print "failed to find best result: %s" % e
    try:
        br = models.Result.objects.filter(competition = comp).exclude(
            pos__lt = 0).exclude(pos_in_grp__lt = 0).order_by('time')[0]
        comp.best_result = br.time
        print br.time
        comp.save()
        return
    except Exception, e:
        print "failed to find best result: %s" % e
        

def reload_persons():
    global all_persons
    all_persons = list(models.Person.objects.all())
    print "loaded %s persons" % len(all_persons)


def new_person_from_rec(result, rec):
    #adding new
    prs = models.Person(name = rec.name,
                        surname = rec.surname,
                        year = rec.year,
                        sex = rec.sex,
                        rank = rec.rank,
                        club = rec.club,
                        city = rec.city)

    prs.save()
    result.person = prs
    result.save()
    all_persons.append(prs)
    print "+",
    sys.stdout.flush() 


def analyse_result(rec):
    print "processing %r" % rec
    result = models.Result(number = rec.number,
                           pos = rec.pos,
                           group = rec.group,
                           pos_in_grp = rec.pos_in_grp,
                           time = rec.time,
                           qualif_rank = rec.qualif_rank,
                           competition = rec.competition,
                           raw_result = rec)
   
    #trying to find such object
    rl = models.Person.objects.filter(surname=rec.surname)

    if rl:
        srl = sorted([(r, measure(rec, r)) for r in rl],
                     lambda a, b: cmp(a[1], b[1]))
        if srl[0][1] == 0:
            print ".choosed %r"%srl[0][0]
            sys.stdout.flush()
            result.person = srl[0][0]
            result.save()
            return None
            
    global all_persons
    srl = sorted(filter(lambda v: v[1]<= THRESHOLD,
                        [(r, measure(rec, r)) for r in all_persons]),
                 lambda a,b: cmp(a[1], b[1]))
    if srl:
        return (result, rec, srl)
    new_person_from_rec(result, rec)
    return None


def resolve(result, rec, srl):
    print "*" * 80
    print "r = %r" % rec

    for pos, (person, measure) in enumerate(srl):
        print "[%s] %r ~ %s" % (pos, person, measure)

    choice = None
    while True:
        try:
            choice = input("choose person ('n' for new): ")
            if choice == 'n':
                new_person_from_rec(result, rec)
                return
            elif -1 < int(choice) < len(srl):
                prs = srl[int(choice)][0]
                result.person = prs
                prs.update_p(rec)
                prs.save()
                result.save()
                return

        except Exception, e:
                print "Failed: %s"%e
    

def process_rlist(rlist):
    for r in rlist:
        r.save()
    
    for r in filter(None, map(analyse_result, rlist)):
        resolve(*r)        

    
def process_rlist_new(rlist):
    for r in rlist:
        r.save()
    comparer.process_rlist(rlist)


def parse_bitza_format(raw):
    """ @param raw: BeautifulSoup match object"""
    col = raw.findAll('td')
    pos = col[0].string
    num = col[1].string
    sname = col[2].contents[0]
    name = col[2].contents[2]
    year = col[3].string
    city = col[4].contents[0]
    club = col[5].string
    time = col[9].string
    return (pos, num, sname, name, year, city, club, time)
    
    
def link_results():
    rl = models.Result.objects.filter(raw_result=None)
    for r in rl:
        try:
            rr = models.RawResult.objects.get(
                competition = r.competition, number = r.number)
            r.raw_result = rr
            r.save()
        except Exception,e:
            print "Could't find %s, %r, %s: %s" % (
                r.competition.id, r.person, r.number, e)
        
    
def recalculate_pos_in_grp(c_id):
    c = models.Competition.objects.get(id=c_id)
    res = models.Result.objects.select_related().filter(competition=c).filter(pos__gte=0).order_by('group')
    rg = itertools.groupby(res,
                           lambda x:x.group)

    srg = [(r[0], sorted(list(r[1]),key=lambda x:x.time)) for r in rg]

    for grp, res in srg:
        pos = 1
        for r in res:
            r.pos_in_grp = pos
            r.save()
            pos += 1
            
            


def validate_person_fields(person):
    """compares persons fields with data in raw_result
    """
    def validate_attr_data(attr, person, results):
        pval = getattr(person, attr)
        results = filter(lambda r:r.raw_result is not None,
                         results)
        alt_vals = sorted([getattr(r.raw_result, attr) for r in results])

        alt_groups = map(lambda (v,l):(v, len(list(l))),
                         itertools.groupby(alt_vals))
        
        alt_groups = sorted(alt_groups,
                            key=lambda (v,c):c,
                            reverse=True)

        if alt_groups[0][1] > 1 and alt_groups[0][0] != pval:
            print person, "attr = %s"%attr
            for pos, (val, cnt) in enumerate(alt_groups):
                print "[%s] %s -- %s times" % (pos, val, cnt)

            choice = None
            while True:
                try:
                    choice = input("choose variant: ")
                    if -1 < int(choice) < len(alt_groups):
                        val = alt_groups[int(choice)][0]
                        setattr(person, attr, val)
                        break
                except Exception, e:
                    print "Failed: %s"%e                

    results = models.Result.objects.filter(person=person)
    if results.count() < 4:
        return

    for attr in ['name', 'surname', 'year' ]:
        validate_attr_data(attr, person, results)


def guess_competition_rating(comp):
    """finds out the competition rating"""
    res_abs = models.Result.objects.filter(
        pos__gt = 0, competition = comp).count()
    res_groups = models.Result.objects.filter(
        pos_in_grp__gt = 0, competition = comp).count()
    if not res_abs and not res_groups:
        print "%s: unknown rating" % comp
        return
    elif res_abs and res_groups:
        comp.rating = models.BOTH_RATING
    elif res_abs:
        comp.rating = models.ABS_RATING
    else:
        comp.rating = models.GROUP_RATING
    comp.save()


def post_process_comp(comp):
    guess_competition_rating(comp)
    find_best_result(comp)
    comp.processed = True
    comp.save()


def find_person_by_surname(surname):
    global all_persons
    srl = sorted(filter(lambda v: v[1]<= 2,
                        [(r, levenshtein(r.surname, surname))
                         for r in all_persons]),
                 lambda a,b: cmp(a[1], b[1]))
    return srl


def process_me_page(url, **defaults):
    """parse maraphon-electro protocol page
    @param url: protocol page
    """
    field_map = {u'Место': POS_IN_GROUP if defaults.has_key('group') else POS,
                 u'Номер': NUM,
                 u'Имя': NAME_SURNAME,
                 u'Год р.': YEAR,
                 u'Команда': CLUB,
                 u'Регион': CITY,
                 u'Результат': TIME} 

    root = html.parse(url, parser = html.HTMLParser(encoding = 'cp1251')).getroot()
    mc = root.get_element_by_id('main_container')
    t = mc[0][3]
    assert(t.tag == 'table')
    head = map(lambda s:s.text.strip(),t[0])
    fields = [field_map.get(f, IGNORE) for f in head]
    rr = map(lambda x:[s.text_content() for s in x], t[1:])
    mrr = parse_list(rr, fields, defaults)
    process_rlist_new(mrr)
    post_process_comp(defaults['competition'])


def process_file(path, fields, competition, **defaults):
    """Читает csv-файл, приводит значения к UNICODE, 
    @param path: путь к .csv-файлу
    @param fields: список полей в файле
    @param defaults: явное задание полей в RawResult
    """
    def decode_utf8(v):
        return v.decode('utf-8')

    defaults['competition'] = competition
    decode_vals = lambda l: map(decode_utf8, l)
    data = map(decode_vals,
               list(csv.reader(open(path), delimiter = ',', quotechar = '"')))
    raw_results = parse_list(data, fields, defaults)
    process_rlist_new(raw_results)
    post_process_comp(competition)
    

    
    
