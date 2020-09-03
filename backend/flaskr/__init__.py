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
  
  # setup CORS, allowing '*' origins
  CORS(app, resources={'/':{'origins':'*'}})
  
  # set Access-Control-Allow
  @app.after_request
  def after_request(response):
    
    # set access control
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true') 
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, PATCH, DELETE, OPTIONS')
    
    return response
  
  # get all available categories
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

  # Get all questions, current category, categories, and number of total questions
  @app.route('/questions')
  def get_questions():
    
    # get all questions
    questions = Question.query.all()
    
    # get all categories
    categories = Category.query.all()

    # paginate questions
    formatted_questions = get_paginated_questions(request, questions)
    
    # format categories
    formatted_categories = [category.format() for category in categories]

    # return status code 404 if no questions found
    if(len(formatted_questions) == 0):
      abort(404)
    
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions)
      'categories': formatted_categories,
      'current_category': list(set([question['category'] for question in formatted_questions]))
    })
    
  # delete a question by question_Id
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      # get question from database
      question = Question.query.get(question_id)
      
      # delete question if found
      question.delete()

      return jsonify({
        'success': True,
        'message': "Question is successfully deleted"
      }),200
      except:
        # return status code 422 for unprocessable operation
        abort(422)
  

  # Add a new question
  @app.route('/questions', methods = ['POST'])
  def create_question():

    # getting JSON data from request
    body = request.get_json()

    answer = body.get('answer', None)
    category = body.get('category', None)
    difficulty = body.get('difficulty', None)
    question = body.get('question', None)
    
    # if any field is empty abort with status code 422
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

  
  # search for a question based on search term and return any question containing it.
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    
    # get search term from json data

    body = request.get_json()
    search_term = body.get('searchTerm', None)
    
    # if empty abort
    if search_term == None:
      abort(422)
    
    try:
      # get all questions containing this search term
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      
      # if not found return not found status code
      if len(questions == 0):
        abort(404)
      
      # if found format questions in result and return them as JSON 
      formatted_questions = get_paginated_questions(request, questions)

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(formatted_questions),
      }), 200

    except:
      abort(404)
  
  
  # get questions based on category using category id.
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    
    # get category from db
    category = Category.query.get(id)
    
    # get questions in this category
    questions = Question.query.filter_by(category=id).all()

    # abort if either questions or category are found
    if questions == None or category == None:
      abort(422)
    
    # if found paginate questions and return them
    formatted_questions = get_paginated_questions(request, questions)

    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions': len(formatted_questions),
      'current_category': category.type
    }), 200

  
  # get random questions to play the quiz 
  @app.route('/quizzes')
  def play_quiz():

    # get request json data
    body = request.get_json()
    
    # get previous question and quiz category 
    previous_questions = body.get('previous_questions')
    quiz_category = body.get('quiz_category')

    # if previous_questions or quiz_category are empty abort with 400 bad request code
    if previous_questions == None or quiz_category == None:
      abort(400)
    
    # get questions in the specified quiz category
    questions = Question.query.filter_by(category = quiz_category['id']).all()

    # randomise next question and make sure it is not a previous one
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
    

  # Create error handlers for all expected errors.   
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

    