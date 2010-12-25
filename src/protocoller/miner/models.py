# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from markitup.fields import MarkupField

(MALE, FEMALE, UNKNOWN) = range(3)
SEX_TYPES = (
    (MALE, u'муж'),
    (FEMALE, u'жен'),
    (UNKNOWN, 'U'),
    ) 

(ABS_RATING, GROUP_RATING, BOTH_RATING) = range(3)
RATING_TYPES = (
    (ABS_RATING, 'абсолютный зачет'),
    (GROUP_RATING, 'зачет по группам'),
    (BOTH_RATING, 'оба')
    )

class Place(models.Model):

    name = models.CharField('Название', max_length = 50)
    slug = models.CharField(max_length = 20, default = '', 
                            db_index = True, unique = True,
                            help_text = 'короткое название для ссылок')
    link = models.URLField('Адрес сайта', null = True, blank = True)
    location = models.CharField('Местоположение', max_length = 200, null = True,
                                blank = True)
    description = MarkupField('Описание', default = '', null = True)
    address = models.CharField('Адрес', max_length=250, default = '', null = True)
    created_by = models.ForeignKey(User, null = True, editable = False,
                                   db_index = True, verbose_name = 'Кем создан')

    def __unicode__(self):
        return self.name

    def get_id(self):
        return self.link_name or self.id

    def get_absolute_url(self):
        return "/place/%s" % (self.slug or self.id)


class SportEvent(models.Model):

    (STATE_NEW, STATE_APPROVED, STATE_HIDDEN) = range(3)
    STATE_TYPES = (
        (STATE_NEW, u'новый'),
        (STATE_APPROVED, u'подтвержден'),
        (STATE_HIDDEN, u'скрыт'),
        )

    place = models.ForeignKey(Place, null=True, blank=True)
    name = models.CharField(max_length=250)
    date = models.DateField(db_index=True)
    end_date = models.DateField(null = True)
    description = models.TextField(default = '', null = True)
    standing = models.TextField(default = '', null = True)
    state = models.IntegerField(choices = STATE_TYPES, default = STATE_NEW)
    last_change = models.DateTimeField(auto_now = True, 
                                      default = datetime.datetime.now(),
                                      editable = False)
    created_by = models.ForeignKey(User, null = True, editable = False)
    registration_open = models.BooleanField(default = False)

    def __unicode__(self):
        return "%s %s"%(self.name, self.date.year)


class Competition(models.Model):

    (CLASSIC_STYLE, FREE_STYLE, DUATHLON) = range(3)
    STYLE_CHOICES = (
        (CLASSIC_STYLE, u'кл.ст.'),
        (FREE_STYLE, u'св.ст.'),
        (DUATHLON, u'дуат-н'),
        )

    (MASS_START, SEP_START) = range(2)
    START_TYPES = (
        (MASS_START, u'мс.ст.'),
        (SEP_START, u'рзд.ст.')
        )    

    event = models.ForeignKey(SportEvent, null=True,
                              related_name="competitions")
    
    
    sex = models.IntegerField(choices=SEX_TYPES, default=UNKNOWN)
    name = models.CharField(max_length=250, blank=True)
    
    style = models.IntegerField(choices=STYLE_CHOICES)
    start_type = models.IntegerField(choices=START_TYPES)
    distance = models.IntegerField()
    link = models.URLField(null=True, blank=True)
    rating = models.IntegerField(choices=RATING_TYPES, default=BOTH_RATING)
    best_result = models.TimeField(null=True, blank=True, default="0:0:0")
    last_change = models.DateTimeField(auto_now = True, 
                                       default = datetime.datetime.now(),
                                       editable = False)
    created_by = models.ForeignKey(User, null = True, editable = False)
    start_time = models.TimeField(null = True)

    def __unicode__(self):
        s = u"%s %s км, %s, %s" % (self.name,                              
                                   self.distance,
                                   self.get_style_display(),
                                   self.get_start_type_display())
        if self.sex != UNKNOWN:
            s = "[%s]"%self.get_sex_display() + s

        return s


(ZMS, MSMK, MS, KMS, R1, R2, R3, NR) = range(8)
RANK_TYPES = (
    (ZMS, u'змс'),
    (MSMK, u'мсмк'),
    (MS, u'мс'),
    (KMS, u'кмс'),
    (R1, u'I'),
    (R2, u'II'),
    (R3, u'III'),
    (NR, u'')
    )

class Person(models.Model):   

    name = models.CharField(max_length=20, default="",
                            null=True, db_index=True)
    
    surname = models.CharField(max_length=30, db_index=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    sex = models.IntegerField(choices=SEX_TYPES, default=UNKNOWN)
    rank = models.IntegerField(choices=RANK_TYPES, default=NR)
    club = models.CharField(max_length=30, default='', null=True, blank=True)
    city = models.CharField(max_length=30, default='', null=True,
                            blank=True, db_index=True)
    
    nickname = models.CharField(max_length=30, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def full_name(self):
        return " ".join(filter(None,
                               [self.surname, self.name]))

    def __unicode__(self):

        return ' '.join(filter(None,[
            self.surname,
            self.name,
            unicode(self.year),
            self.get_rank_display(),
            self.city,
            self.club]))
        
    def update_p(self, p):
        if not self.year and p.year:
            self.year = p.year
        if not self.club and p.club:
            self.club = p.club
        if not self.city and p.city:
            self.city = p.city
        if p.rank < self.rank:
            self.rank = p.rank


(DNS, DNF, DQF) = range(-3, 0)

RESULT_TYPES = ( 
    (DNS, u'dns'),
    (DNF, u'dnf'),
    (DQF, u'dqf')
    )


class RawResult(models.Model):

    (NEW, UPDATED, DELETED) = range(3)

    STATE_CHOICES = ((NEW, 'new'),
                     (UPDATED, 'updated'),
                     (DELETED, 'deleted'))

    competition = models.ForeignKey(Competition, db_index=True,
                                    null=True, blank=True)

    name = models.CharField(max_length=20, default="",
                            null=True, db_index=True)
    surname = models.CharField(max_length=30, db_index=True)
    year = models.IntegerField(null=True, blank=True)
    sex = models.IntegerField(choices=SEX_TYPES, default=UNKNOWN)
    rank = models.IntegerField(choices=RANK_TYPES, default=NR)
    club = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    
    number = models.IntegerField(null=True, blank=True)
    pos = models.IntegerField(default=0)
    group = models.CharField(max_length=20, null=True, blank=True)
    pos_in_grp = models.IntegerField(null=True, blank=True)
    time = models.TimeField()
    qualif_rank = models.IntegerField(choices=RANK_TYPES, default=NR)   

    last_change = models.DateTimeField(auto_now=True)
    state = models.IntegerField(choices=STATE_CHOICES, default=NEW)

    def print_pos(self):
        if not self.pos:
            return ""

        if self.pos < 0:
            return dict(RESULT_TYPES).get(self.pos, "")

        return str(self.pos)

    def __unicode__(self):

        rl = []

        rl.append(self.print_pos())

        if self.group and self.pos_in_grp:
            rl.append("%s[%s]"%(self.pos_in_grp, self.group))

        rl += filter(None,[
            unicode(self.number),
            self.surname,
            self.name,
            unicode(self.year),
            self.get_rank_display(),
            self.city,
            self.club])        
        
        res = u' '.join(rl)

        if self.time:
            res += ' '+self.time.strftime('%H:%M:%S')

        return res


    def full_name(self):
        return " ".join(filter(None,
                               [self.surname, self.name]))

    def print_time(self):
        if self.time:
            return self.time.strftime('%H:%M:%S')
        else:
            return ""
    

class Result(models.Model):    

    person = models.ForeignKey(Person, db_index=True)
    competition = models.ForeignKey(Competition, db_index=True)

    number = models.IntegerField(null=True, blank=True)
    pos = models.IntegerField(default=0)
    group = models.CharField(max_length=20, null=True, blank=True)
    pos_in_grp = models.IntegerField(null=True, blank=True)
    time = models.TimeField()
    qualif_rank = models.IntegerField(choices=RANK_TYPES,
                                      null=True, blank=True)    

    last_change = models.DateTimeField(auto_now=True)

    raw_result = models.ForeignKey(RawResult, null=True, blank=True)

    def print_time(self):
        if self.time:
            return self.time.strftime('%H:%M:%S')
        else:
            return ""


class ImportState(models.Model):

    competition = models.ForeignKey(Competition)
    last_processes = models.IntegerField(default=0)



class PersonFeedback(models.Model):
    person = models.ForeignKey(Person)

    name = models.CharField("Имя", max_length=20, default="",
                            null=True, db_index=True)    
    surname = models.CharField("Фамилия", max_length=30, db_index=True)
    year = models.IntegerField("Год рождения", null=True, blank=True, db_index=True)
    sex = models.IntegerField("Пол", choices=SEX_TYPES, default=UNKNOWN)
    rank = models.IntegerField("Звание", choices=RANK_TYPES, default=NR)
    club = models.CharField("Клуб", max_length=30, default='',
                            null=True, blank=True)
    city = models.CharField("Город", max_length=30, default='', null=True,
                            blank=True, db_index=True)

    wrong_results = models.ManyToManyField(Result, blank=True)


    comment = models.TextField("Комментарий", blank=True)

    contact_email = models.EmailField()
    contact_name = models.CharField(max_length=30)
    
    

class RegistrationInfo(models.Model):
    """Данные, которые оставляет пользователь при регистрации на 
    соревнование. Предполагается, что он регистрирует не только себя, но 
    и других.
    """
    name = models.CharField("Имя", max_length = 20, default = "", null = True)
    surname = models.CharField("Фамилия", max_length=30, db_index=True)
    year = models.IntegerField("Год рождения", null=True, blank=True, db_index=True)
    sex = models.IntegerField("Пол", choices=SEX_TYPES, default=UNKNOWN)
    rank = models.IntegerField("Звание", choices=RANK_TYPES, default=NR)
    club = models.CharField("Клуб", max_length=30, default='',
                            null=True, blank=True)
    city = models.CharField("Город", max_length=30, default='', null=True,
                            blank=True, db_index=True)

    by_user = models.ForeignKey(User, null = True, editable = False, 
                                related_name = 'registrations')
    sport_event = models.ManyToManyField(SportEvent, through = 'RegistrationMembership')


class RegistrationMembership(models.Model):
    """Связывает регистрационные данные и соревнование"""
    info = models.ForeignKey(RegistrationInfo)
    sport_event = models.ForeignKey(SportEvent)
    competition = models.ForeignKey(Competition, null = True)
    date = models.DateTimeField(auto_now = True)





