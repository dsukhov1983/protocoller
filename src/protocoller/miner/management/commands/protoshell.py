from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Creates management console for importing protcols."

    requires_model_validation = False

    def handle(self, *args, **options):
        # XXX: (Temporary) workaround for ticket #1796: force early loading of all
        # models from installed apps.
        from django.db.models.loading import get_models
        loaded_models = get_models()

        from protocoller.miner.models import SportEvent, Competition, Person, MALE, FEMALE
        from protocoller.miner.utils import POS, NUM, GROUP, POS_IN_GROUP, NAME, SURNAME,\
            NAME_SURNAME, YEAR, SEX, RANK, CLUB, CITY, TIME, QUALIF_RANK, IGNORE, \
            process_file, process_me_page

        use_plain = options.get('plain', False)

        import IPython
        # Explicitly pass an empty list as arguments, because otherwise IPython
        # would use sys.argv from this script.
        shell = IPython.Shell.IPShellEmbed(argv=[])
        shell()
        
