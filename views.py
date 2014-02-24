import json, urllib2

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from archives.models import Node, Tag
from archives.functions import tell, login_wrapper, logout_wrapper, edit, delete, edit_tags, process_command
from general.functions import parse_content, json_response

def process(request, text):
    command, text_arguments = process_command(text);
    method = request.META['REQUEST_METHOD']
    arguments = {}
    
    found = True
    if command == 'tell':
        if request.session.has_key('location'):
            arguments['location']=request.session['location']
        arguments['name']=' '.join(text_arguments)
        response, found_node = tell(arguments, method)
        found = True if found_node.title != "idk" else False
    
    elif command == 'login':
        if method == 'POST':
            arguments['username'] = request.POST['username']
            arguments['password'] = request.POST['password']
            arguments['request'] = request
        response = login_wrapper(arguments, method)
    
    elif command == 'logout':
        arguments['request'] = request
        response = logout_wrapper(arguments, method)
    
    elif command in ['edit', 'create']:
        arguments['is_authenticated'] = request.user.is_authenticated
        if method == 'GET':
            if text_arguments[0]:
                arguments['name'] = ' '.join(text_arguments)
        elif method == 'POST':
            arguments['new_name'] = request.POST['name']
            arguments['content'] = request.POST['content']
        if not arguments.has_key('name'):
            arguments['name'] = request.session['location']
        response = edit(arguments, method)

    elif command == 'delete':
        arguments['is_authenticated'] = request.user.is_authenticated
        if text_arguments[0]:
            arguments['name'] = ' '.join(text_arguments)
        else:
            arguments['name'] = request.session['location']
        response = delete(arguments, method)
        arguments.pop('name', None) 
    
    elif command == 'edit_tags':
        arguments['is_authenticated'] = request.user.is_authenticated
        if text_arguments[0]:
            arguments['name'] = ' '.join(text_arguments)
        else:
            arguments['name'] = request.session['location']
        if method == 'POST':
            arguments['tags'] = request.POST['tags'].split(', ')
        response = edit_tags(arguments, method)
    elif command == 'help':
        arguments['name']='help'
        response = tell(arguments, 'GET')
    else:
        arguments['name']='idu'
        response = tell(arguments, 'GET')
        arguments['name']=''
    if arguments.has_key('name'):
        request.session['location'] = arguments['name']
    if found_node:
        request.session['location'] = found_node.title
    return response    


def show(request, name='idk'):
     if request.META['REQUEST_METHOD'] == 'GET':
        n = Node.objects.get(title=name)
        if not n:
            n = Node.objects.get(title='idk')
        context = {'node': n.build_dict()}    

        request.session['location'] = name
        return render(request, 'archives/generic.html', context)
