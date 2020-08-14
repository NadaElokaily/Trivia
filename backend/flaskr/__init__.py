import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['ERROR_404_HELP'] = False
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type,Authorization,true')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET,PATCH,POST,DELETE,OPTIONS')
        return response

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
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        print("entering quiz")
        try:
            data = request.get_json()
            prv_ids = data['previous_question']
            category_id = data['category']
            print("prvids",prv_ids,"category_id",category_id)
            category = Category.query.filter(
                Category.id == category_id).one_or_none()
            # print("cat",category)
            if category is None:
                abort(422)
            all_questions = Question.query.filter(
                Question.category == category_id).all()
            # print("hi")
            all_questions_list = [q.format() for q in all_questions]
            # print("all_questions_list",all_questions_list)
            questions_to_be_asked = []
            # print(len(all_questions_list))
            for q in all_questions_list:
                # print("q",q['id'])
                if q['id'] not in prv_ids:
                    # print("not here", q['id'])
                    q_dict = {}
                    q_dict['id']=q['id'] 
                    q_dict['question']=q['question']
                    q_dict['answer']=q['answer']
                    q_dict['category']=q['category']
                    q_dict['difficulty']=q['difficulty']
                    questions_to_be_asked.append(q)
            # print("questions_to_be_asked",questions_to_be_asked)
            # print("question",questions_to_be_asked[0])
            if len(questions_to_be_asked):
              return jsonify({
                  'question':questions_to_be_asked[0],
                  'quiz questions': questions_to_be_asked
              }), 200
            else:
              print("no further questions")
              return jsonify({
                'quiz questions':[]
              }), 200
        except Exception:
            abort(422)

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route("/categories", methods=['GET'])
    def categories():
        flag404 = False
        print("entering categories", request.method)
        try:
            categories = [cat.format() for cat in Category.query.all()]
            if categories is None:
                print("categories is None")
                flag404 = True
                abort(404)
            categories_dict = {}
            for c in categories:
                categories_dict[c['id']] = c['type']
            return jsonify({
                'categories': categories_dict
            }), 200

        except Exception:
            if flag404:
                abort(404)
            abort(422)

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
    @app.route('/questions', methods=['GET'])
    def questions():
        print("GET questions")
        flag404 = False
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE
            questions = Question.query.all()
            if questions is None:
                print("questions is None")
                flag404 = True
                abort(404)
            questions_dict = [q.format() for q in questions]
            categories = [cat.format() for cat in Category.query.all()]
            categories_dict = {}
            for c in categories:
                categories_dict[c['id']] = c['type']
            current_categories_dict = [
                categories_dict[question['category']] for question in questions_dict[start:end]]

            return jsonify({
                'all categories': categories_dict,
                'all questions': questions_dict,
                'questions': questions_dict[start:end],
                'total number of questions': len(questions_dict),
                'current categories': current_categories_dict
            }), 200

        except Exception:
            if flag404:
                abort(404)
            abort(422)

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_questions(id):
        print("DELETE", id)
        flag404 = False
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if question is None:
                flag404 = True
                abort(404)
            question.delete()
            return jsonify({
                'deleted id': id,
            }), 200
        except Exception:
            if flag404:
                abort(404)
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
    @app.route('/questions', methods=['POST'])
    def add_question():
        print("add_question")
        flag422 = False
        # print(request.form)
        data = request.get_json()
        print("data", data)
        question = data.get('question','')
        answer = data.get('answer','')
        difficulty = data.get('difficulty','')
        category = data.get('category','')

        # .replace(" ", "")
        if ((question.replace(" ", "") == '') or (answer.replace(" ", "") == '') or 
        (difficulty == '') or (category == '')):
            abort(400)
        try:
            questionx = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category)

            questionx.insert()

            return jsonify({
                'added question': question
            }), 200
        except Exception:
            abort(404)

    #  -d '{/"question/":/"hi/",/"answer/":/"hello/",/"difficulty/":/"hard/",/"category/":/"History/"}'
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
    def search():
        page = request.args.get('page', '1', type=int)
        data = request.get_json()
        search_term = data['searchTerm']
        search = "%{}%".format(search_term)
        if search_term == '':
            abort(422)
        try:
            questions = Question.query.filter(
                Question.question.ilike(search)).all()
            if len(questions) == 0:
                abort(404)

            questions_dict = [q.format() for q in questions]

            return jsonify({
                'success': True,
                'questions': questions_dict
            }), 200

        except Exception:
            abort(404)

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<int:category_id>/questions')
    def questions_for_each_category(category_id):
        category = Category.query.filter(
            Category.id == category_id).one_or_none()
        if (category is None):
            abort(422)
        matched_questions = Question.query.filter(
            Question.category == category_id).all()
        questions_dict = [q.format() for q in matched_questions]
        return jsonify({
            'matched category': category.type,
            'questions': questions_dict
        })

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            "Error Code": 403,
            "Error Message": "forbidden"
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "Error Code": 404,
            "Error Message": "Not found"
        }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "Error Code": 500,
            "Error Message": "internal server error"
        }), 500

    @app.errorhandler(422)
    def Unprocessable_Entity(error):
        return jsonify({
            "Error Code": 422,
            "Error Message": "Unprocessable Entity"
        }), 422

    @app.errorhandler(400)
    def Bad_Request(error):
        return jsonify({
            "Error Code": 400,
            "Error Message": "Bad Request"
        }), 400

    return app
