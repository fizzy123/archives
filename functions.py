import urllib2
import logging
import re
from random import choice
from simserver import SessionServer, simserver
log = logging.getLogger(__name__)

from django.core.context_processors import csrf
from django.contrib.auth import authenticate, logout, login
from django.http import HttpResponse

from archives.models import Node, Tag
from general.functions import parse_content, json_response

def tell(arguments, method):
    name = arguments['name']
    if method == 'GET':
        n = None
        location = ''
        if arguments.has_key('location'):
            location = arguments['location']
        while not n:
            if Node.objects.filter(title=location+':'+name).exists():
                n = Node.objects.get(title=location+':'+name)
            elif ':' in location:
                location_array = location.split(":")
                location= ":".join(location_array[:-1])
            else:    
                if Node.objects.filter(title=name).exists():
                    n = Node.objects.get(title=name)
                else:    
                    log.debug('%s not found' % name)
                    n = Node.objects.get(title='idk')
        while n.content[0:3] == '-->':
            if n.content[3:5] == '*.':
                if Tag.objects.filter(title=n.content[5:]).exists():
                    tag = Tag.objects.get(title=n.content[5:])
                    if tag.node_set.all().exists():
                        n = choice(tag.node_set.all())
            else:
                if Node.objects.filter(title=n.content[3::]).exists():
                    n = Node.objects.get(title=n.content[3::])
                else:
                    log.debug('%s not found' % name)
                    n = Node.objects.get(title='idk')
        context = {'reply': parse_content(n.content, 'display'), 'title':n.title}
        return json_response(context), n

service = SessionServer('/mnt/hgfs/Shared/my_server/')
service.stable.model = simserver.SimModel.load("/mnt/hgfs/Shared/wiki")

def parse(arguments, method):
    name = arguments['name']
    if method == 'GET':
        n = None
        while not n:
            matches = service.find_similar({'tokens':re.findall(r"[\w']+", name)},.9)
            if len(matches):
                n = Node.objects.get(pk=matches[0][0])
            else:    
                matches = service.find_similar({'tokens':re.findall(r"[\w']+",name)},.8)
                if len(matches):
                    n = Node.objects.get(pk=matches[0][0])
                else:
                    log.debug('%s not found' % name)
                    n = Node.objects.get(title='idk')
        while n.content[0:3] == '-->':
            if n.content[3:5] == '*.':
                if Tag.objects.filter(title=n.content[5:]).exists():
                    tag = Tag.objects.get(title=n.content[5:])
                    if tag.node_set.all().exists():
                        n = choice(tag.node_set.all())
            else:            
                if Node.objects.filter(title=n.content[3:]).exists():
                    n = Node.objects.get(title=n.content[3:])
            if not n:
                log.debug('%s not found' % name)
                n = Node.objects.get(title='idk')
        context = {'reply': parse_content(n.content, 'display'), 'title':n.title}
        return json_response(context), n

def login_wrapper(arguments, method):
    if method == 'GET':
        context = {'form': {'username':'', 'password':''}}
    elif method == 'POST':
        user = authenticate(username=arguments['username'],password=arguments['password'])
        if user:
            login(arguments['request'],user)
            context = {'reply':'Welcome, %s.' % user.username}
        else:
            context = {'reply':'I could not find anyone with that combination of username and password. Please try again.'}
    return json_response(context)    

def logout_wrapper(arguments, method):
    if arguments['request'].user.is_authenticated():
        if method=='GET':
            logout(arguments['request'])
            context = {'reply':'You\'ve been logged out successfully. Have a good day.'}
            return json_response(context)
    else:
        return tell({'name':'idk'}, 'GET')[0]

def edit(arguments, method):
    if arguments['is_authenticated']:
        name = arguments['name']
        n = Node.objects.get_or_create(title=name)[0]
        if method == 'GET':
            context = {}
            context['reply'] = 'Please make your changes.'
            context['form'] = {'content':parse_content(n.content, 'edit'), 'name':n.title}

        elif method == 'POST':
            n.content = parse_content(arguments['content'],'edit')
            n.title = arguments['new_name']
            n.save()
            
            context = {}
            context['reply'] = 'Thank you. Your revisions to %s have been recorded.' % name
        return json_response(context)
    else:
        return tell({'name':'idk'}, 'GET')[0]

def delete(arguments, method):
    if arguments['is_authenticated']:
        if method == 'POST':
            n = Node.objects.get(title=arguments['name'])
            tag_list = n.tags.all()
            for tag in tag_list:
                if not len(tag.node_set.all()):
                    tag.delete()
            n.delete()
            context = {}
            context['reply'] = 'Thank you. %s has been removed from the archives.' % arguments['name'] 
            return json_response(context)
    else:
        return tell({'name':'idk'}, 'GET')[0]
        
def edit_tags(arguments, method):
    if arguments['is_authenticated']:
        n = Node.objects.get(title=arguments['name'])
        if method == 'GET':
            tags = ''
            for tag in n.tags.all():
                tags += tag.title + ', '
            tags = tags[0:-2]    
            context = {}
            context['reply'] = 'Please edit the tags below.'
            context['form'] = {'tags':tags}
        elif method == 'POST':
            n.set_tags(arguments['tags'])
            context = {}
            context['reply'] = 'Thank you. The tags for %s have been updated.' % arguments['name']
        return json_response(context)           
    else:
        return tell({'name':'idk'}, 'GET')[0]

def process_command(text):
    text = urllib2.unquote(text.decode("utf8"))
    #text = text.replace('your ','Nobel:')
    #text = text.replace('\'s ',':')
    text = text.replace('?','')
    text = text.replace('.','')
    text = text.lower()
    text = text.split(' ')
    removable_words = ['me', 'about', 'the', 'us', 'a', 'an']
    if text[0] == "what's":
        command = 'process'
        text_arguments =["what", "is"] + text[1:]
    elif text[0] in ['tell','edit','login','logout','delete','edit_tags', 'help']:  
        command = text[0]
        text_arguments = text[1:]
    elif text[0] == 'show':
        command = 'tell'
        text_arguments = text[1:]
    else:
        command = 'process'
        text_arguments = text
    text_arguments = filter(lambda x: x not in removable_words, text_arguments)
    return command, text_arguments

def index_nodes():
    print "loading server"
    service = SessionServer('/mnt/hgfs/Shared/my_server/')
    print "loading model"
    service.open_session()
    service.session.drop_index()
    service.session.model = simserver.SimModel.load("/mnt/hgfs/Shared/wiki")
    print service.session.model
    print "loading nodes"
    nodes = Node.objects.all()
    print "Building corpus"
    corpus = [{'id':node.pk,'tokens':re.findall(r"[\w']+",node.question.lower())} for node in nodes]
    print "indexing corpus"
    service.index(corpus)
    print service.stable.keys
    service.commit()
