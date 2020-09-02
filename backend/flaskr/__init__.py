import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def get_paginated_questions(request,selection):
  page = request.args.get('page', 1, type = int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  formated_questions = questions[start:end]

  return formated_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={'/':{'origins':'*'}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    
    # set access control
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true') 
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, PATCH, DELETE, OPTIONS')
    
    return response
  
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_all_categories():

    try:
      categories = Category.query.all()
      formated_categories = [category.format() for category in categories]
      return jsonify({
        'success': True,
        'categories': formated_categories,
        'total_categories': len(formated_categories)
      }),200
    except:
      abort(500)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
  
    questions = Question.query.all()
    categories = Category.query.all()

    formatted_questions = get_paginated_questions(request, questions)
    formatted_categories = [category.format() for category in categories]

    if(len(formatted_questions) == 0):
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions)
      'categories': formatted_categories,
      'current_category': list(set([question['category'] for question in formatted_questions]))
    })
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()

      return jsonify({
        'success': True,
        'message': "Question is successfully deleted"
      }),200
      except:
        abort(422)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods = ['POST'])
  def create_question():
    body = request.get_json()

    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)
    question = body.get('question', None)

    if ((question == None) or (answer == None) or (difficulty == None) or (category == None)):
        abort(422)
    
    try:
      question = Question(question, answer, category, difficulty)
      question.insert()

      return jsonify({
        'success': True,
        'message': 'Question is successfully created'
      }),201
      except:
        abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm', None)
    
    if search_term == None:
      abort(422)
    
    try:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

      if len(questions == 0):
        abort(404)
      
      formatted_questions = get_paginated_questions(request, questions)

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(formatted_questions),
      }), 200

    except:
      abort(404)
  
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    category = Category.query.get(id)
    questions = Question.query.filter_by(category=id).all()

    if questions == None or category == None:
      abort(422)
    
    formatted_questions = get_paginated_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': category.type
    }), 200

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes')
  def play_quiz():
    body = request.get_json()

    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')

    if previous_questions == None or quiz_category == None:
      abort(400)
    
    questions = Question.query.filter_by(category = quiz_category['id']).all()

    next_question = questions[random.randint(0, len(questions)-1)]

    prev = True
    while prev:
      if next_question.id in previous_questions:
        next_question = questions[random.randint(0, len(questions)-1)]
      else:
        prev = False
    
    return jsonify({
      'success': True,
      'question': next_question.format()
    }), 200
    


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.error_handler(400)
  def bad_request(error):
    return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request error'
    }), 400
  
  @app.error_handler(404)
  def not_found(error):
    return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocesable_entity(error):
    return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable entity'
    }), 422
  
  @app.error_handler(500)
  def Internal_server_error(error):
    return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
    }), 500

  
  
  return app

    