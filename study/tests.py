import json
from django.test import TestCase
from django.test.client import Client


class StudyTest(TestCase):
    """Completely black-box tests the study json / http-POST interfaces
    """

    fixtures = ['vocab50.json']
    def login_client(self,client):
	response = c.post('/login/', {'username': 'john', 'password': 'smith'})
	self.assertEqual(response.status_code,200)

    def prepare_lesson(self,client,lessonnum):
	response = c.post("/deck/reset")
	self.assertEqual(response.status_code,200)

	response = c.post("/study/lesson/%s/" % lessonnum)
	self.assertEqual(response.status_code,200)
	

    def check_qa(self, client, question, answer)
	"""Checks that /study/getqa returns this q/a pair.
	returns the parsed json object in full
	"""
	response = client.post('/study/getqa')
	self.assertEqual(response.status_code,200)
	jsonstr = response.content
	qa = json.loads(jsonstr)
	self.assertEqual(qa['question'],'house')
	self.assertEqual(qa['answer'],'casa')
	return qa


    def post_impression(self, client, answer, qa)
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

	qa = self.check_qa(c, 'house', 'casa')
	self.post_impression(c, 'Yes')

	qa = self.check_qa(c, 'chicken', 'pollo')
	self.post_impression(c, 'Yes')


