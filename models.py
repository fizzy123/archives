from django.db import models

from general.functions import parse_content

class Tag(models.Model):
    title = models.CharField(max_length=200, primary_key=True)

    def __unicode__(self):
        return self.title

class Node(models.Model):
    title = models.CharField(max_length=200, default='idk', unique=True)
    content = models.TextField(default='Teach me')
    question = models.TextField(default='')
    tags = models.ManyToManyField(Tag, blank = True)
    
    def __unicode__(self):
        return self.title

    def build_dict(self, mode=''):
        node_dict = {}
        node_dict['title'] = self.title
        node_dict['tags'] = ''
        if self.tags:
            for tag in self.tags.all():
                node_dict['tags'] += tag.title + ', '
            node_dict['tags'] = node_dict['tags'][0:-2]    
        if mode:
            node_dict['content'] = parse_content(self.content, mode)
        else:
            node_dict['content'] = self.content
        return node_dict   

    def set_tags(self, tags):
        old_tag_list = list(self.tags.all())
        self.tags.clear()
        for tag in tags:
            t = Tag.objects.get_or_create(title=tag)
            self.tags.add(t[0])
            t[0].save()
            self.save()
        self.save()
        for tag in old_tag_list:
            if not len(tag.node_set.all()):
                tag.delete()
        return self        
