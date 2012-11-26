# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Work.is_archived'
        db.add_column('dreamdiary_work', 'is_archived', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Task.is_archived'
        db.add_column('dreamdiary_task', 'is_archived', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Adding field 'Network.is_archived'
        db.add_column('dreamdiary_network', 'is_archived', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Work.is_archived'
        db.delete_column('dreamdiary_work', 'is_archived')

        # Deleting field 'Task.is_archived'
        db.delete_column('dreamdiary_task', 'is_archived')

        # Deleting field 'Network.is_archived'
        db.delete_column('dreamdiary_network', 'is_archived')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 22, 0, 7, 43, 635390)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 9, 22, 0, 7, 43, 635294)'}),
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
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
