# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Diary'
        db.create_table('dreamdiary_diary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('dreamdiary', ['Diary'])

        # Adding model 'UserGroup'
        db.create_table('dreamdiary_usergroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('dreamdiary', ['UserGroup'])

        # Adding model 'Network'
        db.create_table('dreamdiary_network', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='networks', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('color', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['dreamdiary.Color'], null=True, blank=True)),
            ('hierarchy', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('order', self.gf('dreamdiary.fields.OrderField')(null=True, blank=True)),
        ))
        db.send_create_signal('dreamdiary', ['Network'])

        # Adding unique constraint on 'Network', fields ['order', 'user']
        db.create_unique('dreamdiary_network', ['order', 'user_id'])

        # Adding M2M table for field usergroups on 'Network'
        db.create_table('dreamdiary_network_usergroups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('network', models.ForeignKey(orm['dreamdiary.network'], null=False)),
            ('usergroup', models.ForeignKey(orm['dreamdiary.usergroup'], null=False))
        ))
        db.create_unique('dreamdiary_network_usergroups', ['network_id', 'usergroup_id'])

        # Adding model 'Task'
        db.create_table('dreamdiary_task', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default=u'Task', max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tasks', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('color', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['dreamdiary.Color'], null=True, blank=True)),
            ('order', self.gf('dreamdiary.fields.OrderField')(null=True, blank=True)),
        ))
        db.send_create_signal('dreamdiary', ['Task'])

        # Adding model 'Work'
        db.create_table('dreamdiary_work', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='works', to=orm['auth.User'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('color', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['dreamdiary.Color'], null=True, blank=True)),
            ('order', self.gf('dreamdiary.fields.OrderField')(null=True, blank=True)),
        ))
        db.send_create_signal('dreamdiary', ['Work'])

        # Adding unique constraint on 'Work', fields ['user', 'order']
        db.create_unique('dreamdiary_work', ['user_id', 'order'])

        # Adding model 'TaskAttachment'
        db.create_table('dreamdiary_taskattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=2048)),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['dreamdiary.Task'])),
        ))
        db.send_create_signal('dreamdiary', ['TaskAttachment'])

        # Adding model 'WorkAttachment'
        db.create_table('dreamdiary_workattachment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=2048)),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(related_name='attachments', to=orm['dreamdiary.Work'])),
        ))
        db.send_create_signal('dreamdiary', ['WorkAttachment'])

        # Adding model 'Color'
        db.create_table('dreamdiary_color', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('color', self.gf('dreamdiary.fields.HtmlColorCodeField')(max_length=7)),
            ('title', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='colors', to=orm['auth.User'])),
        ))
        db.send_create_signal('dreamdiary', ['Color'])

        # Adding unique constraint on 'Color', fields ['color', 'user']
        db.create_unique('dreamdiary_color', ['color', 'user_id'])

        # Adding model 'Connection'
        db.create_table('dreamdiary_connection', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('network', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dreamdiary.Network'])),
            ('task', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dreamdiary.Task'])),
            ('order', self.gf('dreamdiary.fields.OrderField')(null=True, blank=True)),
        ))
        db.send_create_signal('dreamdiary', ['Connection'])

        # Adding unique constraint on 'Connection', fields ['network', 'task']
        db.create_unique('dreamdiary_connection', ['network_id', 'task_id'])

        # Adding unique constraint on 'Connection', fields ['network', 'task', 'order']
        db.create_unique('dreamdiary_connection', ['network_id', 'task_id', 'order'])

        # Adding model 'Answer'
        db.create_table('dreamdiary_answer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('connection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dreamdiary.Connection'])),
            ('work', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dreamdiary.Work'])),
            ('submitted', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dreamdiary', ['Answer'])

        # Adding unique constraint on 'Answer', fields ['connection', 'work']
        db.create_unique('dreamdiary_answer', ['connection_id', 'work_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Answer', fields ['connection', 'work']
        db.delete_unique('dreamdiary_answer', ['connection_id', 'work_id'])

        # Removing unique constraint on 'Connection', fields ['network', 'task', 'order']
        db.delete_unique('dreamdiary_connection', ['network_id', 'task_id', 'order'])

        # Removing unique constraint on 'Connection', fields ['network', 'task']
        db.delete_unique('dreamdiary_connection', ['network_id', 'task_id'])

        # Removing unique constraint on 'Color', fields ['color', 'user']
        db.delete_unique('dreamdiary_color', ['color', 'user_id'])

        # Removing unique constraint on 'Work', fields ['user', 'order']
        db.delete_unique('dreamdiary_work', ['user_id', 'order'])

        # Removing unique constraint on 'Network', fields ['order', 'user']
        db.delete_unique('dreamdiary_network', ['order', 'user_id'])

        # Deleting model 'Diary'
        db.delete_table('dreamdiary_diary')

        # Deleting model 'UserGroup'
        db.delete_table('dreamdiary_usergroup')

        # Deleting model 'Network'
        db.delete_table('dreamdiary_network')

        # Removing M2M table for field usergroups on 'Network'
        db.delete_table('dreamdiary_network_usergroups')

        # Deleting model 'Task'
        db.delete_table('dreamdiary_task')

        # Deleting model 'Work'
        db.delete_table('dreamdiary_work')

        # Deleting model 'TaskAttachment'
        db.delete_table('dreamdiary_taskattachment')

        # Deleting model 'WorkAttachment'
        db.delete_table('dreamdiary_workattachment')

        # Deleting model 'Color'
        db.delete_table('dreamdiary_color')

        # Deleting model 'Connection'
        db.delete_table('dreamdiary_connection')

        # Deleting model 'Answer'
        db.delete_table('dreamdiary_answer')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 21, 23, 58, 7, 611784)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 21, 23, 58, 7, 611689)'}),
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
        'dreamdiary.answer': {
            'Meta': {'unique_together': "(('connection', 'work'),)", 'object_name': 'Answer'},
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dreamdiary.Connection']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'submitted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dreamdiary.Work']"})
        },
        'dreamdiary.color': {
            'Meta': {'unique_together': "(('color', 'user'),)", 'object_name': 'Color'},
            'color': ('dreamdiary.fields.HtmlColorCodeField', [], {'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'colors'", 'to': "orm['auth.User']"})
        },
        'dreamdiary.connection': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('network', 'task'), ('network', 'task', 'order'))", 'object_name': 'Connection'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'network': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dreamdiary.Network']"}),
            'order': ('dreamdiary.fields.OrderField', [], {'null': 'True', 'blank': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dreamdiary.Task']"})
        },
        'dreamdiary.diary': {
            'Meta': {'object_name': 'Diary'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'dreamdiary.network': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('order', 'user'),)", 'object_name': 'Network'},
            'color': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['dreamdiary.Color']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'hierarchy': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'order': ('dreamdiary.fields.OrderField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'networks'", 'to': "orm['auth.User']"}),
            'usergroups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dreamdiary.UserGroup']", 'null': 'True', 'blank': 'True'})
        },
        'dreamdiary.task': {
            'Meta': {'ordering': "['order']", 'object_name': 'Task'},
            'color': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['dreamdiary.Color']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('dreamdiary.fields.OrderField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "u'Task'", 'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tasks'", 'to': "orm['auth.User']"})
        },
        'dreamdiary.taskattachment': {
            'Meta': {'object_name': 'TaskAttachment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['dreamdiary.Task']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2048'})
        },
        'dreamdiary.usergroup': {
            'Meta': {'object_name': 'UserGroup'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'dreamdiary.work': {
            'Meta': {'ordering': "['order']", 'unique_together': "(('user', 'order'),)", 'object_name': 'Work'},
            'color': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['dreamdiary.Color']", 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('dreamdiary.fields.OrderField', [], {'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'works'", 'to': "orm['auth.User']"})
        },
        'dreamdiary.workattachment': {
            'Meta': {'object_name': 'WorkAttachment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '2048'}),
            'work': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'attachments'", 'to': "orm['dreamdiary.Work']"})
        }
    }

    complete_apps = ['dreamdiary']
