# -*- coding: utf-8 -*-
import os
import sys
import datetime
import logging
import itertools

from functools import partial

from protocoller.miner import models


RESULT_VARIANTS = (
    (models.DNS, [u'dns', u'не старт']),
    (models.DNF, [u'dnf', u'сошел', u'сошла', u'не фин']),
    (models.DQF, [u'dqf', u'дискв'])
    )


# A simple HTML table parser. It turns tables (including nested tables) into arrays
# Nigel Sim <nigel.sim@gmail.com>
# http://simbot.wordpress.com
from HTMLParser import HTMLParser
import re, string, os
from string import lower

class Table(list):
    pass
	
class Row(list):
    pass

class Cell(object):
    def __init__(self):
        self.data = None
        return
    def append(self,item):
        if self.data != None:
	    print "Overwriting %s"%self.data
        self.data = item

# Get the item on the top of a stack
def top(x):
    return x[len(x)-1]

class TableParser(HTMLParser):
    def __init__(self, parser=None):
        """
	The parser is a method which will be passed the doc at the end
	of the parsing. Useful if TableParser is within an inner loop and
	you want to automatically process the document. If it is omitted then
	it will do nothing
	"""
        self._tag = None
	self._buf = None
	self._attrs = None
	self.doc = None # Where the document will be stored
	self._stack = None
	self._parser = parser
	self.reset()
        return

    def reset(self):
        HTMLParser.reset(self)
	self.doc = []
	self._stack = [self.doc]
	self._buf = ''

    def close(self):
        HTMLParser.close(self)
	if self._parser != None:
	    self._parser(self.doc)

    def handle_starttag(self, tag, attrs):
        self._tag = tag
	self._attrs = attrs
	if lower(tag) == 'table':
	    self._buf = ''
            self._stack.append(Table())
	elif lower(tag) == 'tr':
	    self._buf = ''
            self._stack.append(Row())
	elif lower(tag) == 'td':
	    self._buf = ''
            self._stack.append(Cell())
	
        #print "Encountered the beginning of a %s tag" % tag

    def handle_endtag(self, tag):
	if lower(tag) == 'table':
	    t = None
	    while not isinstance(t, Table):
                t = self._stack.pop()
	    r = top(self._stack)
            r.append(t)

	elif lower(tag) == 'tr':
	    t = None
	    while not isinstance(t, Row):
                t = self._stack.pop()
	    r = top(self._stack)
            r.append(t)

	elif lower(tag) == 'td':
	    c = None
	    while not isinstance(c, Cell):
                c = self._stack.pop()
	    t = top(self._stack)
	    if isinstance(t, Row):
	        # We can not currently have text and other table elements in the same cell. 
		# Table elements get precedence
	        if c.data == None:
                    t.append(self._buf)
		else:
		    t.append(c.data)
	    else:
	        print "Cell not in a row, rather in a %s"%t
        self._tag = None
        #print "Encountered the end of a %s tag" % tag

    def handle_data(self, data):
        self._buf += data


class ST:

    def __init__(self, func, name):
        """
        @param func:str-> atr value
        @param name attr name
        """
        self.func = func
        self.name = name

    def __call__(self, obj, val):
        try:
            setattr(obj, self.name, self.func(val))
        except Exception, e:
            print "Error till parsing field %s for obj %r: %s" %(
                self.name, obj, e)
            
        

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
    if val:
        return int(val)
    else:
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
    except Exception, e:
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

def parser_func(rec, func_map, defaults={}):
    """parses plain record by giving description"""
    
    res = models.RawResult()

    for id, tp in func_map.items():        
        _parse_map[tp](res, rec[id])

    for name, value in defaults.items():
        setattr(res, name, value)    

    return res

def parse_list(rlist, func_map, defaults={}):

    return [parser_func(r, func_map, defaults) for r in rlist]

(POS, NUM, GROUP, POS_IN_GROUP, NAME, SURNAME, NAME_SURNAME,
 YEAR, SEX, RANK, CLUB, CITY, TIME, QUALIF_RANK) = range(14)

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
    TIME: time_parse}
    

func_map = { 0: POS,
             1: NUM,
             3: NAME_SURNAME,
             4: YEAR,
             5: RANK,
             6: CITY,
             7: CLUB,
             8: TIME,
             11: QUALIF_RANK}


equivalence_sets = (u'ао', u'её', u'оё', u'зс', u'гк', u'бп', u'ий', u'бп',
                    u'щш')

_equiv_map = {}

for s in equivalence_sets:
    for c in s:
        _equiv_map[c] = _equiv_map.get(c,[]) + list(s)

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
     
    # alist = filter(None, [a.city, a.club])
#     blist = filter(None, [b.city, b.club])

#     if alist and blist:
#         res += min([levenshtein(x,y) for x,y in combinations(alist, blist)])

    return res

    
THRESHOLD = 4 #recognize threshold


all_persons = list(models.Person.objects.all())

def find_best_result(comp_id):
    try:
        comp = models.Competition.objects.get(id=comp_id)
        br = models.Result.objects.get(competition=comp, pos=1)
        comp.best_result = br.time
        comp.save()
        return
    except Exception,e:
        print "failed to find best result for %s: %s"%(comp_id,e)

    try:
        comp = models.Competition.objects.get(id=comp_id)
        br = models.Result.objects.filter(competition=comp).exclude(pos__lt=0).exclude(pos_in_grp__lt=0).order_by('time')[0]
        comp.best_result = br.time
        comp.save()
        return
    except Exception,e:
        print "failed to find best result for %s: %s"%(comp_id,e)
        
        

def reload_persons():
    global all_persons
    all_persons = list(models.Person.objects.all())
    print "loaded %s persons" % len(all_persons)


def process_raw_result_list(rlist):    
    
    for r in rlist:
        process_raw_result(r)

def process_raw_result(rec):


    def resolve(result, rec, srl):
        
        print "_______________________"
        print "r = %r" % rec

        for pos, (person, measure) in enumerate(srl):
            print "[%s] %r ~ %s" % (pos, person, measure)
            

        choice = None
        while True:
            try:
                choice = input("choose person ('n' for new): ")

                if choice == 'n':
                    return False
                elif -1 < int(choice) < len(srl):
                    prs = srl[int(choice)][0]
                    result.person = prs
                    prs.update_p(rec)
                    prs.save()
                    result.save()
                    return True                
                    
            except Exception, e:
                print "Failed: %s"%e

        
            
    
    print "processing %r"%rec

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
            return 
            

    global all_persons

    if all_persons:

        srl = sorted(filter(lambda v: v[1]<= THRESHOLD,
                     [(r, measure(rec, r)) for r in all_persons]),
                     lambda a,b: cmp(a[1], b[1]))

        if srl and resolve(result, rec, srl):
            return        

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
    print "+"
    sys.stdout.flush()
                        
    

def parse_bitza_format(raw):
    """
    @param raw: BeautifulSoup match object
    """

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
            rr = models.RawResult.objects.filter(competition = r.competition,
                                               number = r.number)[0]
            r.raw_result = rr
            r.save()
        except Exception,e:
            print "Could't find %s, %r, %s: %s"%(r.competition.id,
                                                 r.person,
                                                 r.number,
                                                 e)
        
    
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
