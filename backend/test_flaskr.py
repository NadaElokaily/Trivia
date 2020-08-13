import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

# from utils import create_mock_question


class TriviaAPITestCase(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:12345678@{}/{}".format('localhost:5432', self.database_name)

        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(data['success'],True)        
        self.assertTrue(data['all categories'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']),10)
        self.assertTrue(data['total number of questions'],len(data['all questions']))
        self.assertTrue(data['current categories'])

    def test_not_Found_category(self):
        response = self.client().get('/categories/11/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)

    def test_quiz(self):
        quiz_data = {'previous_question': [16,17,18],'category': 2}        
        response = self.client().post('/quiz', json=quiz_data)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['quiz questions'])
        self.assertEqual(data['quiz questions'][0]['id'], 19)

    def test_delete_question(self):
        question_id = '13'
        path_to_question_to_be_deleted = '/questions/'+question_id
        response = self.client().delete(path_to_question_to_be_deleted)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(data['deleted id'],question_id)

    def test_delete_not_found_question(self):
        response = self.client().delete('/questions/100')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)

    def test_search_question(self):
        request_data = {
            'searchTerm': "name is Cassius Clay?",        }

        response = self.client().post('/questions/search', json=request_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_not_found_search_term(self):
        searchTerm = {'searchTerm': 'dreamsbergtown'}
        response = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
    
    def test_empty_search_term(self):
        searchTerm = {'searchTerm': ''}
        response = self.client().post('/questions/search', json=searchTerm)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)

    def test_create_question(self):
        question_to_be_created = {'question': 'yada','answer': 'yada','difficulty': 3,'category': 4}
        response = self.client().post('/questions', json=question_to_be_created)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['added question'], question_to_be_created['question'])

    def get_certain_category_questions(self):
        response = self.client().get('/categories/3/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['matched category'], 'Geography')
        self.assertEqual(len(data['questions']), 1)

if __name__ == "__main__":
    unittest.main()