import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app           = create_app()
        self.client        = self.app.test_client
        self.database_name = 'trivia_test'
        self.database_path = f'postgres://postgres:admin@localhost:5432/{self.database_name}'

        setup_db(self.app, self.database_path)

        self.test_new_question = {
            'question'  : 'test question?',
            'answer'    : 'test answer',
            'difficulty': 1,
            'category'  : 5,
        }

        self.test_new_question_none = {
            'question'  : 'test question?',
            'answer'    : 'test answer',
            'difficulty': 1,
            'category'  : None,
        }

        self.test_new_question_empty_string = {
            'question'  : 'test question?',
            'answer'    : '',
            'difficulty': 1,
            'category'  : 5,
        }

        self.test_play_quiz = {
            'previous_questions': [],
            'quiz_category': {
                'id': 5,
                'type': 'Entertainment'
            }
        }

        self.test_play_quiz_none= {
            'previous_questions': None,
            'quiz_category': {
                'id': 1000,
                'type': 'no category'
            }
        }

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
        """
        Checks for:
            - status code : 200.
            - success : true.
            - length of the returned categories.
            - message : Categories retrieved successfully.
        """
        res  = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['message'], 'Categories retrieved successfully')

    def test_get_paginated_questions(self):
        """
        Checks for:
            - status code : 200.
            - success : true.
            - total questions returned.
            - length of the returned questions.
            - length of the returned categories.
            - message : Categories & questions retrieved successfully.
        """
        res  = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertEqual(data['message'], 'Categories & questions retrieved successfully')

    def test_422_sent_requesting_of_minus_page_number(self):
        """
        Checks for:
            - status code : 422.
            - success : false.
            - message : Unprocessable Entity.
        """
        res  = self.client().get('/questions?page=-1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_404_sent_requesting_beyond_valid_page(self):
        """
        Checks for:
            - status code : 404.
            - success : false.
            - message : Resource not Found.
        """
        res  = self.client().get('/questions?page=1999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_delete_question(self):
        """
        Checks for:
            - status code : 200.
            - success : true.
            - message : The question deleted successfully.
        """
        init_test_new_que = self.client().post('/questions', json=self.test_new_question)
        test_new_que_id = json.loads(init_test_new_que.data)['created']

        res = self.client().delete(f'/questions/{test_new_que_id}')
        data = json.loads(res.data)

        question = Question.query.filter_by(id=test_new_que_id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'The question deleted successfully')
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exist(self):
        """
        Checks for:
            - status code : 404.
            - success : false.
            - message : Resource not Found.
        """
        res  = self.client().delete('/question/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not Found')

    def test_create_new_question(self):
        """
        Checks for:
            - status code : 201.
            - success : true.
            - id of the new created question.
            - message : The question created successfully.
        """
        res  = self.client().post('/questions', json=self.test_new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(data['message'], 'The question created successfully')

    def test_400_if_question_creation_not_allowed(self):
        """
        Checks for:
            - status code : 400.
            - success : false.
            - message : Bad Request.
        """
        res  = self.client().post('/questions', json=self.test_new_question_none)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')
    
    def test_422_if_question_creation_not_allowed(self):
        """
        Checks for:
            - status code : 422.
            - success : false.
            - message : Unprocessable Entity.
        """
        res  = self.client().post('/questions', json=self.test_new_question_empty_string)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_get_question_search_with_results(self):
        """
        Checks for:
            - status code : 200.
            - success : true.
            - Total questions returned.
            - questions length : 10.
            - message : the questions searched found successfully.
        """
        res = self.client().post('/questions', json={'searchTerm': 'a'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['message'], 'the questions searched found successfully')

    def test_get_book_search_without_results(self):
        """
        Checks for:
            - status code : 200.
            - success : true.
            - Total questions returned: false.
            - questions length : 0.
            - message : the questions searched found successfully.
        """
        res = self.client().post('/questions', json={'searchTerm': 'applejacks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(data['total_questions'])
        self.assertEqual(len(data['questions']), 0)
        self.assertEqual(data['message'], 'the questions searched found successfully')

    def test_get_questions_by_category(self):
        """
        Checks for:
            - status code : 200.
            - success : true.
            - Total questions returned: true.
            - questions length : 10.
        """
        res = self.client().get('categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_get_questions_by_none_category(self):
        """
        Checks for:
            - status code : 422.
            - success : false.
            - message: Unprocessable Entity.
        """
        res = self.client().get('categories/8/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_play_quiz(self):
        """
        Checks for:
            - status code : 200.
            - success : true.
            - the returned next question.
        """
        res  = self.client().post('/quizzes', json=self.test_play_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_questions_by_none_category(self):
        """
        Checks for:
            - status code : 422.
            - success : false.
            - message: Unprocessable Entity.
        """
        res = self.client().post('/quizzes', json=self.test_play_quiz_none)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()