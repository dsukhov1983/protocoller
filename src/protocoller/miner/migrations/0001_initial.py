# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Place'
        db.create_table('miner_place', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('link_name', self.gf('django.db.models.fields.CharField')(default='', max_length=20, db_index=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('miner', ['Place'])

        # Adding model 'SportEvent'
        db.create_table('miner_sportevent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('place', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.Place'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', null=True)),
            ('standing', self.gf('django.db.models.fields.TextField')(default='', null=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 12, 16, 23, 58, 55, 65994), auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('miner', ['SportEvent'])

        # Adding model 'Competition'
        db.create_table('miner_competition', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='competitions', null=True, to=orm['miner.SportEvent'])),
            ('sex', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('style', self.gf('django.db.models.fields.IntegerField')()),
            ('start_type', self.gf('django.db.models.fields.IntegerField')()),
            ('distance', self.gf('django.db.models.fields.IntegerField')()),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('rating', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('best_result', self.gf('django.db.models.fields.TimeField')(default='0:0:0', null=True, blank=True)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2010, 12, 16, 23, 58, 55, 66920), auto_now=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
        ))
        db.send_create_signal('miner', ['Competition'])

        # Adding model 'Person'
        db.create_table('miner_person', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, db_index=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('club', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, db_index=True, blank=True)),
            ('nickname', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
        ))
        db.send_create_signal('miner', ['Person'])

        # Adding model 'RawResult'
        db.create_table('miner_rawresult', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.Competition'], null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, db_index=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('club', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pos', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('pos_in_grp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('qualif_rank', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('state', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('miner', ['RawResult'])

        # Adding model 'Result'
        db.create_table('miner_result', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.Person'])),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.Competition'])),
            ('number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pos', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('pos_in_grp', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('time', self.gf('django.db.models.fields.TimeField')()),
            ('qualif_rank', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('last_change', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('raw_result', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.RawResult'], null=True, blank=True)),
        ))
        db.send_create_signal('miner', ['Result'])

        # Adding model 'ImportState'
        db.create_table('miner_importstate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('competition', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.Competition'])),
            ('last_processes', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('miner', ['ImportState'])

        # Adding model 'PersonFeedback'
        db.create_table('miner_personfeedback', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['miner.Person'])),
            ('name', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, db_index=True)),
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=30, db_index=True)),
            ('year', self.gf('django.db.models.fields.IntegerField')(db_index=True, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('rank', self.gf('django.db.models.fields.IntegerField')(default=7)),
            ('club', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(default='', max_length=30, null=True, db_index=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('miner', ['PersonFeedback'])

        # Adding M2M table for field wrong_results on 'PersonFeedback'
        db.create_table('miner_personfeedback_wrong_results', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('personfeedback', models.ForeignKey(orm['miner.personfeedback'], null=False)),
            ('result', models.ForeignKey(orm['miner.result'], null=False))
        ))
        db.create_unique('miner_personfeedback_wrong_results', ['personfeedback_id', 'result_id'])


    def backwards(self, orm):
        
        # Deleting model 'Place'
        db.delete_table('miner_place')

        # Deleting model 'SportEvent'
        db.delete_table('miner_sportevent')

        # Deleting model 'Competition'
        db.delete_table('miner_competition')

        # Deleting model 'Person'
        db.delete_table('miner_person')

        # Deleting model 'RawResult'
        db.delete_table('miner_rawresult')

        # Deleting model 'Result'
        db.delete_table('miner_result')

        # Deleting model 'ImportState'
        db.delete_table('miner_importstate')

        # Deleting model 'PersonFeedback'
        db.delete_table('miner_personfeedback')

        # Removing M2M table for field wrong_results on 'PersonFeedback'
        db.delete_table('miner_personfeedback_wrong_results')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'miner.competition': {
            'Meta': {'object_name': 'Competition'},
            'best_result': ('django.db.models.fields.TimeField', [], {'default': "'0:0:0'", 'null': 'True', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'distance': ('django.db.models.fields.IntegerField', [], {}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'competitions'", 'null': 'True', 'to': "orm['miner.SportEvent']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 12, 16, 23, 58, 55, 66920)', 'auto_now': 'True', 'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'rating': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'start_type': ('django.db.models.fields.IntegerField', [], {}),
            'style': ('django.db.models.fields.IntegerField', [], {})
        },
        'miner.importstate': {
            'Meta': {'object_name': 'ImportState'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.Competition']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_processes': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'miner.person': {
            'Meta': {'object_name': 'Person'},
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'club': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'db_index': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'miner.personfeedback': {
            'Meta': {'object_name': 'PersonFeedback'},
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'club': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'comment': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'db_index': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.Person']"}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'wrong_results': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['miner.Result']", 'symmetrical': 'False', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'})
        },
        'miner.place': {
            'Meta': {'object_name': 'Place'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'link_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'db_index': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'miner.rawresult': {
            'Meta': {'object_name': 'RawResult'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'club': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.Competition']", 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'db_index': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pos_in_grp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'qualif_rank': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'rank': ('django.db.models.fields.IntegerField', [], {'default': '7'}),
            'sex': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '30', 'db_index': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'miner.result': {
            'Meta': {'object_name': 'Result'},
            'competition': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.Competition']"}),
            'group': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.Person']"}),
            'pos': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pos_in_grp': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'qualif_rank': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'raw_result': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.RawResult']", 'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.TimeField', [], {})
        },
        'miner.sportevent': {
            'Meta': {'object_name': 'SportEvent'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_change': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2010, 12, 16, 23, 58, 55, 65994)', 'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['miner.Place']", 'null': 'True', 'blank': 'True'}),
            'standing': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['miner']
