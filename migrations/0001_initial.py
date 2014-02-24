# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table(u'archives_tag', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
        ))
        db.send_create_signal(u'archives', ['Tag'])

        # Adding model 'Node'
        db.create_table(u'archives_node', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(default='idk', unique=True, max_length=200)),
            ('content', self.gf('django.db.models.fields.TextField')(default='Teach me')),
        ))
        db.send_create_signal(u'archives', ['Node'])

        # Adding M2M table for field tags on 'Node'
        m2m_table_name = db.shorten_name(u'archives_node_tags')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('node', models.ForeignKey(orm[u'archives.node'], null=False)),
            ('tag', models.ForeignKey(orm[u'archives.tag'], null=False))
        ))
        db.create_unique(m2m_table_name, ['node_id', 'tag_id'])


    def backwards(self, orm):
        # Deleting model 'Tag'
        db.delete_table(u'archives_tag')

        # Deleting model 'Node'
        db.delete_table(u'archives_node')

        # Removing M2M table for field tags on 'Node'
        db.delete_table(db.shorten_name(u'archives_node_tags'))


    models = {
        u'archives.node': {
            'Meta': {'object_name': 'Node'},
            'content': ('django.db.models.fields.TextField', [], {'default': "'Teach me'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['archives.Tag']", 'symmetrical': 'False', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'default': "'idk'", 'unique': 'True', 'max_length': '200'})
        },
        u'archives.tag': {
            'Meta': {'object_name': 'Tag'},
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'})
        }
    }

    complete_apps = ['archives']