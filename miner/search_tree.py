# -*- coding: utf-8 -*-
import sys

from collections import defaultdict
from itertools import chain, groupby
from operator import itemgetter

from protocoller.miner import models


class SearchTree:
    
    def __init__(self):
        self.children = defaultdict(SearchTree)
        self.is_leaf = False
        self.links = []

    def __contains__(self, w):
        if not self.children.has_key(w[0]):
            return False
        d = self.children[w[0]]
        if len(w) == 1:
            return d.is_leaf
        return w[1:] in d

    def add_word(self, w, obj = None):
        d = self.children[w[0]]
        if len(w) > 1:
            d.add_word(w[1:], obj)
        else:
            d.is_leaf = True
            if obj is not None:
                d.links.append(obj)


    def has_letter(self, l):
        return self.children.has_key(l)


    def get(self, w, default=None):
        if not self.children.has_key(w[0]):
            return default
        d = self.children[w[0]]
        if len(w) == 1:
            return d
        return d.get(w[1:], default)


def gen_misprints(s, pos):
    """прототип функции, искажающей слово
    @param s: строка
    @param pos: текущая позиция
    @return список (s, pos)
    """
    pass


SOUNDLIKE_SET = (u'ао', u'еёоя', u'зс', u'гк', u'бп', u'ий', u'бп', u'жщш',
                 u'иы', u'кл', u'еи', u'сч', u'тс', u'мн', u'фв', u'дт')

WRITESLIKE_SET = (u'аоя', u'еёя', u'иы', u'сч', u'нк',  u'зд', u'чн', u'дц')

VOWEL_SET = (u'йуеёыаоэяию', u'цкнгшщзхфвпрлджчмтб')

ANYLETTER_SET = (u'йцукенгшщзхъфывапролджэячсмитьбю',)


class MisprintBySetGen:
    """Геренирует искажения слов, основываясь на отношении эквивалентности
    между буквами"""

    def __init__(self, equiv_set):
        self._equiv_map = defaultdict(set)

        for el in equiv_set:
            for l in el:
                self._equiv_map[l] = self._equiv_map[l].union(set(el))
        for k, v in self._equiv_map.iteritems():
            v.remove(k)


    def __call__(self, s, pos):
        return map(lambda c:(s[:pos] + c + s[pos+1:], pos), self._equiv_map[s[pos]])


def letter_omission_gen(s, pos):
    """пропуск буквы"""
    if pos + 1 == len(s):
        return [(s[:-1], pos-1)]
    return [(s[:pos] + s[pos+1:], pos)]


def swap_gen(s, pos):
    """заменяет текущую и последующую буквы"""
    if len(s) == pos + 1:
        return []
    
    return [(s[:pos] + s[pos+1] + s[pos] + s[pos+2:], pos)]

def idle_gen(s, pos):
    """ничего не меняет"""
    return [(s,pos)]

def insert_get(s, pos):
    """вставляет произвользую букву"""
    return map(lambda c:(s[:pos] + c + s[pos:], pos), ANYLETTER_SET[0])


class Combinator:
    """Подбирает опечатки"""


    def __init__(self):

        self._gens = ((MisprintBySetGen(SOUNDLIKE_SET), 0.3),
                      (MisprintBySetGen(WRITESLIKE_SET), 0.5),
                      (MisprintBySetGen(VOWEL_SET), 0.6),
                      (MisprintBySetGen(ANYLETTER_SET), 1.),
                      (letter_omission_gen, 1.),
                      (insert_get, 1.0),
                      (swap_gen, 1.),
                      (idle_gen, 0.))



    def guess(self, st, s, pos, threshold, penalty = 0.):
        if penalty > threshold:
            return []
        if pos >= len(s):
            if st.is_leaf:
                #maybe better return st here
                return [(st, penalty)]
            return []

        #gen misprints
        variants = list(chain(*map(lambda (o,p):[(r,p) for r in o(s, pos)], self._gens)))
        #order, group by and minimize by penalty
        keyfunc = itemgetter(0)
        variants = [(ns, npos, penalty + min(map(itemgetter(1), vals)))
                    for (ns, npos), vals in groupby(sorted(variants, key = keyfunc), keyfunc)]
        
        return list(chain(*[self._process_variant(st, ns, np, threshold, pen) for ns, np, pen in variants]))
        
    def _process_variant(self, st, s, pos, threshold, penalty):
        if st.has_letter(s[pos]):
            return self.guess(st.children[s[pos]], s, pos + 1, threshold, penalty)
        return []
            




class SmartComparer:

    def __init__(self, agree_thr = 1.0, filter_thr = 6.0):
        self.agree_thr = agree_thr
        self.filter_thr = filter_thr
        self.persons = list(models.Person.objects.all())
        #build search tree by surname
        self.st = SearchTree()
        for p in self.persons:
            self.st.add_word(p.surname, p)
            
        self.combinator = Combinator()


    def process_rlist(self, rlist):
        for r in filter(None, map(self.process_result, rlist)):
            print
            self.ask_user(*r)


    def ask_user(self, result, rec, candidates):
        print ">"
        print "r = %r" % rec
        for pos, (person, measure) in enumerate(candidates):
            print "[%s] %r ~ %s" % (pos + 1, person, measure)

        choice = None
        while True:
            try:
                choice = raw_input("choose person('n' for new): ")

                if choice == 'n':
                    p = self.add_new_person(rec)
                    result.person = p
                    result.save()
                    return
                elif 0 < int(choice) <= len(candidates):
                    person = candidates[int(choice)-1][0]
                    result.person = person
                    person.update_p(rec)
                    person.save()
                    result.save()
                    return
            except Exception, e:
                print "Failed: %s" % e



    def add_new_person(self, rec):
        person = models.Person(name = rec.name,
                               surname = rec.surname,
                               year = rec.year,
                               sex = rec.sex,
                               rank = rec.rank,
                               club = rec.club,
                               city = rec.city)

        person.save()
        self.persons.append(person)
        self.st.add_word(person.surname, person)
        return person

    def process_result(self, rec):
        sys.stdout.flush()
        result = models.Result(number = rec.number,
                               pos = rec.pos,
                               group = rec.group,
                               pos_in_grp = rec.pos_in_grp,
                               time = rec.time,
                               qualif_rank = rec.qualif_rank,
                               competition = rec.competition,
                               raw_result = rec)


        #first check exactly this person
        r = self.st.get(rec.surname, None)
        if r is not None:
            candidates = sorted(filter(None, [self.check_candidate(rec, p, 0.) for p in r.links]),
                                key=itemgetter(1))
            if candidates and candidates[0][1] == 0.:
                #founded exactly right person
                person = candidates[0][0]
                result.person = person
                result.save()
                person.update_p(rec)
                person.save()
                sys.stdout.write(".")
                return

        #founded all persons with likely surnames
        variants = self.combinator.guess(self.st, rec.surname, 0, self.filter_thr)
        #variants = [(st, penalty)] transform it to [(person, penalty)],
        #make uniq by person and order by penalty
        variants = [(p, min(map(itemgetter(1), vals)))
                    for p, vals in groupby(sorted([(p, pen) for st, pen in variants for p in st.links],
                                                  key = itemgetter(0)), itemgetter(0))]
        variants = sorted(variants, key = itemgetter(1))


        if len(variants) == 0:
            #no variants -- do add new person
            p = self.add_new_person(rec)
            result.person = p
            result.save()
            sys.stdout.write("+")
            return 

        #firstly verify persons with penalty <= agree_thr
        var_iter = groupby(variants, lambda o:o[1] <= self.agree_thr)
        good_variants = var_iter.next()[1]

        candidates = sorted(filter(None, [self.check_candidate(rec, p, pen) for p, pen in good_variants]),
                            key = itemgetter(1))

        if candidates:
            if candidates[0][1] == 0.:
                #founded exactly right person
                person = candidates[0][0]
                result.person = person
                result.save()
                person.update_p(rec)
                person.save()
                sys.stdout.write(".")
                return
            #get list of persons on agreement threshold
            agree_list = filter(lambda o:o[1] <= self.agree_thr, candidates)
            if len(agree_list) == 1:
                #we have exactly one variant
                result.person = agree_list[0][0]
                result.save()
                sys.stdout.write(".")
                return
            #we have more than one agreement_candidate -- human decision
            #if we already asking user, so check all other persons in variants list
            
        try:
            other_variants = var_iter.next()[1]
        except StopIteration:
            other_variants = []
            
        candidates += sorted(filter(None, [self.check_candidate(rec, p, pen) for p, pen in other_variants]),
                             key = itemgetter(1))

        if len(candidates) == 0:
            #no variants -- do add new person
            p = self.add_new_person(rec)
            result.person = p
            result.save()
            sys.stdout.write("+")
            return 

        sys.stdout.write("?")
        #return candidates for human decision
        return (result, rec, candidates)
            
    
    def check_candidate(self, rec, person, penalty):
        """сличаем имя и дату рождения"""
        if len(rec.name) > 1 and len(person.name) > 1 and rec.name != person.name:
            name_st = SearchTree()
            name_st.add_word(person.name)
            v = sorted(self.combinator.guess(name_st, rec.name, 0, self.filter_thr, penalty),
                       key = itemgetter(1))
            if not v:
                return
            penalty += v[0][1]

        #compare year
        if rec.year >= 1900 and person.year >= 1900 and rec.year != person.year:
            penalty += float(min(6, abs(person.year - rec.year)))/2.0

        if penalty <= self.filter_thr:
            return (person, penalty)
            
