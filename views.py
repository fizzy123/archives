import json, urllib2
import logging
log = logging.getLogger(__name__)

#from clockwork import clockwork
#api = clockwork.API('API_KEY_GOES_HERE')

from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django_socketio import broadcast_channel

from archives.models import Response
from general.functions import json_response

def index(request):
    return render(request, 'archives/index.html')

def recieve(request):
    message = request.POST['message']
    response, created = Response.objects.get_or_create(message = message)
    if created:
        response.save()
        message = clockwork.SMS(
            to = '6786974205', 
            message = message)
        api.send(message)
        response = json_response({'channel':response.pk})
    else:
        response = json_response({'reply': reponse.reply})

    return response    

def reply(request):
    reply = request.GET['content']
    response = Response.objects.filter(reply=None).order_by('created')[0]
    response.reply = reply
    response.save()
    broadcast(response.reply, channel=response.pk)
    return HttpResponse()
