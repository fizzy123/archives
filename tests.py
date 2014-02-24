import json, urllib2

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from archives.models import Node, Tag

class ArchivesViewTest(TestCase):
    def authenticate(self):
        self.client.login(username='user1',password='user1_pw')

    def get_process(self, command, args={}, reverse_url='archives:process'):
        arguments = urllib2.quote(command.encode("utf8"))
        response = self.client.get(reverse(reverse_url, args=(arguments,)), args)
        return json.loads(response.content)

    def post_process(self, command, args={}, reverse_url='archives:process'):
        arguments = urllib2.quote(command.encode("utf8"))
        response = self.client.post(reverse(reverse_url, args=(arguments,)), args)
        return json.loads(response.content)

    def setUp(self):
        user1 = User.objects.create_user('user1','user1@test.com','user1_pw')
        node1 = Node(title='Intro', content = 'Hello. How can I help you?')
        node3 = Node(title='idk', content = 'I\'m sorry. I don\'t understand that.')
        node1.save()

        node1.set_tags(['conversation', 'voice'])
        self.get_process('tell Intro')

    def test_process_tell_view(self):
        response = self.get_process('tell Intro')   
        self.assertEqual(response['reply'], 'Hello. How can I help you?')

    def test_process_redirect_tell_view(self):
        node = Node(title='target', content='target content')
        node.save()

        node = Node(title='redirect', content='-->target')
        node.save()

        response = self.get_process('tell redirect')
        self.assertEqual(response['reply'], 'target content')

    def test_show_view(self):
        response = self.client.get(reverse('archives:show', args=('Intro',)))
        self.assertEqual(response.context['node']['content'],'Hello. How can I help you?')
        self.assertEqual(response.context['node']['tags'],'conversation, voice')

    def test_process_login_get_view(self):
        response = self.get_process('login')

        self.assertEqual(response['form']['username'],'')
        self.assertEqual(response['form']['password'],'')
    
    def test_process_successful_login_post_view(self):
        response = self.post_process('login', {'username':'user1','password':'user1_pw'})
        self.assertEqual(response['reply'],'Welcome, user1.')
        self.assertIn('_auth_user_id', self.client.session)

    def test_process_unsuccessful_login_post_view(self):
        response = self.post_process('login', {'username':'user','password':'user_pw'})
        self.assertEqual(response['reply'],'I could not find anyone with that combination of username and password. Please try again.')

    def test_process_logout_view(self):
        self.authenticate()
        response = self.post_process('logout')
        self.assertEqual(response['reply'],'You\'ve been logged out successfully. Have a good day.')
        self.assertNotIn('_auth_user_id', self.client.session)
    
    def test_process_edit_view(self):
        node = Node(title='Nobel Yoo', content = 'Nobel Yoo is a total loser')
        node.save()
        self.authenticate()
        response = self.get_process('edit Nobel Yoo')
        self.assertEqual(response['reply'],'Please make your changes.')
        self.assertEqual(response['form']['name'], 'Nobel Yoo')
        self.assertEqual(response['form']['content'],'Nobel Yoo is a total loser')

        response = self.post_process('edit Nobel Yoo', {'name':'Seon Yoo','content':'Seon YOo is a total loser'})
        self.assertEqual(response['reply'],'Thank you. Your revisions to Seon Yoo have been recorded.')
        n = Node.objects.get(title="Seon Yoo")
        self.assertEqual(n.content,'Seon YOo is a total loser')

    def test_process_create_get_view(self):    
        self.authenticate()
        response = self.get_process('create test')
        self.assertEqual(response['reply'],'Please make your changes.')
        self.assertEqual(response['form']['name'], 'test')
        self.assertEqual(response['form']['content'], 'Teach me')

    def test_process_delete_view(self):
        node = Node(title='help', content = 'I\'m sorry. I don\'t understand that.')
        node.save()
        self.authenticate()
        response = self.post_process('delete help')
        self.assertEqual(response['reply'], 'Thank you. help has been removed from the archives.')
        self.assertEqual(list(Node.objects.filter(title='help')), [])

    def test_process_edit_tags_get_view(self):
        self.authenticate()
        response = self.get_process('edit_tags Intro')
        self.assertEqual(response['reply'],'Please edit the tags below.')
        self.assertEqual(response['form']['tags'],'conversation, voice') 

    def test_process_edit_tags_post_view(self):
        node = Node(title='even', content='placeholder for even tags')
        node.save()

        self.authenticate()
        response = self.post_process('edit_tags even', {'tags':'two, for, six'})
        self.assertEqual(response['reply'], 'Thank you. The tags for even have been updated.')
        tags = Node.objects.get(title='even').tags.all()
        tags = [tag.title for tag in tags]
        self.assertIn('two',tags)
        self.assertIn('for',tags)
        self.assertIn('six',tags)

        response = self.post_process('edit_tags even', {'tags':'two, four, six'})
        tags = Node.objects.get(title='even').tags.all()
        tags = [tag.title for tag in tags]
        self.assertIn('two',tags)
        self.assertIn('four',tags)
        self.assertIn('six',tags)
        self.assertNotIn('for',tags)

