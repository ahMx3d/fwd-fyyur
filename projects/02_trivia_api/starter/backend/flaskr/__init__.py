from logging import error
import os
from re import search
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random, sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_rows(request, rows):
  """
  Paginates the database retrieved rows with
  each page number from the request arguments.
  """
  page  = request.args.get('page', 1, type=int)
  if (page <= 0):
    error = 400
    sys.exit(error)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end   = start + QUESTIONS_PER_PAGE

  formatted_rows = [row.format() for row in rows]
  current_rows   = formatted_rows[start:end]

  return current_rows

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  # connect the application to the database
  setup_db(app)
  # the cross origin resources setup
  CORS(app, resources={r'*': {'origins': '*'}})

  # the CORS access control headers
  @app.after_request
  def after_request(response):
    '''
    Sets headers Access-Control-Allow.
    '''
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization, true'
    )
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET, POST, PATCH, DELETE, OPTIONS'
    )
    return response

  # fetch all categories
  @app.route('/categories')
  def get_categories():
    """
    Handles GET requests for all available categories, and
    returns a dictionary of each category's id and type
    in the format of key: value pairs.
    """
    error = None
    try:
      cates = Category.query.all()
      error = 404; return sys.exit() if (len(cates) == 0) else jsonify({
        'success'   : True,
        'status'    : 200,
        # 'categories': [cate.format() for cate in cates],
        'categories': {cate.id:cate.type for cate in cates},
        'message'   : 'Categories retrieved successfully'
      }), 200
    except:
      abort(404) if (error == 404) else abort(500)

  @app.route('/questions')
  def get_questions():
    """
    Handles GET requests for questions including pagination (every 10 questions), and
    returns list of questions, number of total questions, current category, categories.
    """
    error = None
    try:
      total_questions    = Question.query.order_by(Question.id.desc()).all()
      questions_per_page = paginate_rows(request, total_questions)
      total_categories   = Category.query.order_by(Category.id.desc()).all()
      
      error = 404; return sys.exit() if ((len(questions_per_page) == 0 or len(total_categories) == 0)) else jsonify({
        'success'         : True,
        'status'          : 200,
        'questions'       : questions_per_page,
        'total_questions' : len(total_questions),
        'current_category': None,
        # 'categories'      : [Category.format() for Category in total_categories],
        'categories'      : {Category.id:Category.type for Category in total_categories},
        'message'         : 'Categories & questions retrieved successfully'
      }), 200
    except:
      abort(404) if (error == 404) else abort(422)

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    """
    Handles DELETE question using a question ID.
    """
    error = None
    try:
      question = Question.query.filter_by(id=question_id).one_or_none()
      if question is None:
        error = 404
        sys.exit()
      else:
        question.delete()
        return jsonify({
          'success': True,
          'status' : 200,
          'message': 'The question deleted successfully'
        }), 200
    except:
      abort(404) if (error == 404) else abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
    """
    Handles get questions based on a search term.
    Handles POST a new question, which will require the question and answer text, category, and difficulty score.
    Returns any questions for whom the search term is a substring of the question. 
    Returns the newly created question id.
    """
    error      = None
    body       = request.get_json()
    search     = body.get('searchTerm', None)
    question   = body.get('question', None)
    answer     = body.get('answer', None)
    difficulty = body.get('difficulty', None)
    category   = body.get('category', None)
    values     = [question, answer, difficulty, category]
    try:
      if search:
        if '' in values:
          error = 422
          return sys.exit()
        else:
          total_questions = Question.query.order_by(
            Question.id
          ).filter(
            Question.question.ilike(f'%{search}%')
          ).all()
          current_questions = paginate_rows(
            request,
            total_questions
          )

          return jsonify({
            'success'        : True,
            'status'         : 200,
            'questions'      : current_questions,
            'total_questions': len(total_questions),
            'message'        : 'the questions searched found successfully'
          }), 200
      else:
        if None in values:
          error = 400
          return sys.exit()
        if '' in values:
          error = 422
          return sys.exit()

        new_question = Question(
          question   = question,
          answer     = answer,
          difficulty = difficulty,
          category   = category
        )
        new_question.insert()

        return jsonify({
          'success': True,
          'status' : 201,
          'created': new_question.id,
          'message': 'The question created successfully'
        }), 201
    except:
      abort(400) if (error == 400) else abort(422)

  @app.route('/categories/<int:cate_id>/questions')
  def get_cate_questions(cate_id):
    '''
    Handles a GET request to get questions based on category, and 
    returns list of all paginated questions for each page.
    '''
    error = None
    try:
      category = Category.query.filter_by(id=cate_id).one_or_none()
      if category is None:
        error = 422
        return sys.exit()
      else:
        total_questions = Question.query.filter_by(category=cate_id).order_by(Question.id.desc()).all()
        current_questions = paginate_rows(
          request,
          total_questions
        )
        return jsonify({
          'success'         : True,
          'status'          : 200,
          'questions'       : current_questions,
          'total_questions' : len(total_questions),
          'current_category': category.id,
          # 'current_category': category.type,
          # 'current_category': {category.id:category.type},
          'message'         : f'the questions of category "{category.type}" found successfully'
        })
    except:
      abort(422) if (error == 422) else abort(404)

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    '''
    Handles a POST request to get questions to play the quiz. 
    This endpoint takes category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions.
    '''
    error     = None
    body      = request.get_json()
    prev_ques = body.get('previous_questions', None)
    quiz_cate = body.get('quiz_category', None)

    try:
      if ((quiz_cate is None) or (prev_ques is None)):
        error = 422
        return sys.exit()
      else:
        ques = Question.query.all() if (quiz_cate['id'] == 0) else Question.query.filter_by(
          category=quiz_cate['id']
          ).all()

        available_ques = [que.format() for que in ques if que.id not in prev_ques]
        next_que       = random.choice(available_ques) if (len(available_ques) > 0) else None

        return jsonify({
          "success"         : True,
          "status"          : 200,
          "question"        : next_que
        }), 200
    except:
      abort(422) if (error == 422) else abort(404)

  @app.errorhandler(400)
  def bad_request(error):
    '''
    Handles error 400
    '''
    return jsonify({
        'success': False,
        'error':400,
        'message':'Bad Request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    '''
    Handles error 404
    '''
    return jsonify({
        'success': False,
        'error':404,
        'message':'Resource not Found'
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    '''
    Handles error 405
    '''
    return jsonify({
        'success': False,
        'error':405,
        'message':'Method not Allowed'
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    '''
    Handles error 422
    '''
    return jsonify({
        'success': False,
        'error':422,
        'message':'Unprocessable Entity'
    }), 422

  @app.errorhandler(500)
  def unprocessable(error):
    '''
    Handles error 500
    '''
    return jsonify({
        'success': False,
        'error':500,
        'message':'Internal Server Error'
    }), 500
  
  return app