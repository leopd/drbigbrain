try: import simplejson as json
except ImportError: import json
from django.test import TestCase
from django.test.client import Client


class StudyTest(TestCase):
    """Completely black-box tests the study json / http-POST interfaces
    """

    #fixtures = ['trivial.json']
    fixtures = ['vocab50.json']
    def login_client(self,client):
	#response = client.post('/accounts/login/', {'username': 'richard', 'password': 'abcd0123'})
	#self.assertEqual(response.status_code,200)
	# above works, but below is faster, cleaner
	client.login(username='richard', password='abcd0123')

	# Check that login succeeded
	response = client.post('/ajaxloginlink')
	self.assertEqual(response.status_code,200)
	#print response.content
	self.failUnless(response.content.find('Welcome back') >= 0 )


    def prepare_lesson(self,client,lessonnum):
	response = client.get("/deck/reset")
	self.assertEqual(response.status_code,302)

	response = client.get("/study/lesson/%s/" % lessonnum)
	self.assertEqual(response.status_code,302)
	

    def check_qa(self, client, question, answer):
	"""Checks that /study/getqa returns this q/a pair.
	returns the parsed json object in full
	"""
	response = client.post('/study/getqa')
	self.assertEqual(response.status_code,200)
	jsonstr = response.content
	qa = json.loads(jsonstr)
	self.assertEqual(qa['question'],question)
	self.assertEqual(qa['answer'],answer)
	return qa


    def post_impression(self, client, answer, qa):
	"""posts an impression response with the specified answer.
	"""
	response = client.post('/study/impression', {
				'answer': answer,
				'id': qa['id'],
			      })
	self.assertEqual(response.status_code,200)



    def test_getqa(self):
	c = Client()
	self.login_client(c)
	self.prepare_lesson(c,1)

	#qa = self.check_qa(c, 'house', 'casa') # trivial fixture
	qa = self.check_qa(c, '(unicode)4f60', '<i>n(unicode)01d0</i><br/>You')
	self.post_impression(c, 'Yes', qa)

	#qa = self.check_qa(c, 'chicken', 'pollo') # trivial fixture
	qa = self.check_qa(c, '(unicode)597d', '<i>h(unicode)01ceo</i><br/>good; well; fine; O.K.')
	#{"pk": 2, "model": "flashcards.concept", "fields": {"description": "good; well; fine; O.K. / (unicode)597d / h(unicode)01ceo"}},

	#self.post_impression(c, 'Yes', qa)


