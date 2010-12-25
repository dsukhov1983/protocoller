from protocoller.miner import models
from django.contrib import admin

class RawResultAdmin(admin.ModelAdmin):

    list_display = ('competition', 'pos', 'group', 'pos_in_grp',
                    'number', 'full_name',
                    'rank', 'year', 'print_time')

    search_fields = ['surname']


admin.site.register(models.RawResult, RawResultAdmin)


class CompetitionAdmin(admin.ModelAdmin):

    raw_id_fields = ('event',)
    list_display = ('id', 'event', 'name', 'sex', 'style', 'distance')
    list_display_links = ('id', 'name')
    ordering = ('-event__date',)

admin.site.register(models.Competition, CompetitionAdmin)


class SportEventAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'date')
    #ordering = ('-date',)

admin.site.register(models.SportEvent, SportEventAdmin)

class ResultsInline(admin.TabularInline):
    model = models.Result
    list_display = ('id', 'competition', )
    raw_id_fields = ('raw_result', 'person', 'competition')

class PersonAdmin(admin.ModelAdmin):
    inlines = [ResultsInline,]
    list_display = ('id', 'full_name', 'rank', 'year', 'city', 'club')
    search_fields = ['surname']


admin.site.register(models.Person, PersonAdmin)

class ResultAdmin(admin.ModelAdmin):

    list_display = ('id', 'competition', 'pos',
                    'number', 'person', 'print_time')
    
    search_fields = ['person__surname']

    raw_id_fields = ('person', 'raw_result')

    list_select_related = True
    

admin.site.register(models.Result, ResultAdmin)

admin.site.register(models.ImportState)



class PlaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'slug', 'name')
admin.site.register(models.Place, PlaceAdmin)


class PersonFeedbackAdmin(admin.ModelAdmin):
    raw_id_fields = ('person', 'wrong_results')

    list_display = ('person', 'contact_name')

admin.site.register(models.PersonFeedback, PersonFeedbackAdmin)
