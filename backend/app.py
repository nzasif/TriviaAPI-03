from flask import request, abort, jsonify
import random
from flask_cors import CORS

from setup import db, app
from models import Question, Category
from utils import get_paginated_qs

# setting CORS for the app
CORS(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
    return response

# get request for categories
@app.route('/categories')
def get_categories():
    categories_list = Category.query.order_by(Category.id).all()
    
    if len(categories_list) == 0:
        abort(404)

    return jsonify ({
        'success': True,
        'categories': {item.id: item.type for item in categories_list}
    })
    
# This endpoint will return questions list
@app.route('/questions')
def get_trivia_questions():
    try:
        qsQuery = Question.query.order_by(Question.id).all()

        current_qs = get_paginated_qs(request, qsQuery)

        all_categories = Category.query.all()

        total_qs = len(qsQuery)

        if total_qs == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_qs,
            'total_questions': total_qs,
            'current_category': [],
            'categories': [cat.type for cat in all_categories],
        }), 200
    except:
        bad_request(400)


# remove question by id
@app.route('/questions/<int:question_id>', methods=['DELETE'])
def remove_question(question_id):
    try:
        q = Question.query.filter(Question.id == question_id).one_or_none()

        # if there is no question then show 404 page
        if q == None:
            abort(404)
            
        # delete the question
        q.delete()

        # after deleting the question, requery the questions
        qsQuery = Question.query.order_by(Question.id).all()
            
        # paginate them before returning
        current_qs = get_paginated_qs(request, qsQuery)
            
        return jsonify({
            'success': True,
            'deleted': question_id,
            'questions': current_qs,
            'total_questions': len(qsQuery)
        })

    except Exception:
        abort(422)
    
# POST a new question, and return new paginated list of questions
@app.route('/questions', methods=['POST'])
def add_new_question():
    # get json from the request body
    req_body = request.get_json()

    # get individual fields from the request body
    new_q = req_body.get('question', None)
    new_ans = req_body.get('answer', None)
    new_cat = req_body.get('category', None)
    new_difficulty = req_body.get('difficulty', None)

    try:
        ## initialize a new question
        question = Question(
        question = new_q,
        answer = new_ans,
        category = new_cat,
        difficulty = new_difficulty
       )
        # insert it into the db
        question.insert()

        # after inerting new question, re query the questions again
        qsQuery = Question.query.order_by(Question.id).all()
            
        current_qs = get_paginated_qs(request, qsQuery)

        qs_count = len(Question.query.all())

        return jsonify({
            'success': True,
            'questions': current_qs,
            'total_questions': qs_count
        })
                
    except Exception:
        abort(422)
    
@app.route('/search')
def search_question():
    try:
        req_body = request.get_json()
        search = req_body.get('searchTerm', None)

        if search:
            qs = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
            current_qs = [question.format() for question in qs]
            total_qs = len(current_qs)

        return jsonify({
            'success': True,
            'questions': current_qs,
            'total_questions': total_qs,
        })           
    except:
        bad_request(400)
            
# get questions of a specific category
@app.route('/categories/<int:cat_id>/questions')
def questions_in_cat(cat_id):
    try:
        qsQuery = Question.query.filter(cat_id == Question.category).all()
    
        current_qs = get_paginated_qs(request, qsQuery)

        all_categories = Category.query.all()
            
        qs_list = list(current_qs)

        if cat_id > len(all_categories):
            abort(404)

        return jsonify({
                "success": True,
                "questions": qs_list,
                "total_questions": len(qsQuery),
                "current_category": [cat.type for cat in all_categories if cat.id == cat_id ]
            })
    except:
        abort(404)

@app.route('/quizzes', methods=['POST'])
def start_trivia_quizz():
    try:
        req_body = request.get_json()
        quiz_category = req_body.get('quiz_category')
        prev_qs = req_body.get('previous_questions')
        cat_id = quiz_category['id']
            
        if cat_id == 0:
            qs = Question.query.filter(Question.id.notin_(prev_qs)).all()
        else:
            qs = Question.query.filter(Question.id.notin_(prev_qs), 
            Question.category == cat_id).all()
                
        q = None

        if(qs):
            q = random.choice(qs)

        return jsonify({
            'success': True,
            'question': q.format()
        })
    except:
        abort(422)

# 404 Error handler
@app.errorhandler(404)
def not_found(error):
    return( 
        jsonify({'success': False, 'error': 404,'message': 'requested resource not found'}),
        404
    )
    
# 422 error handler
@app.errorhandler(422)
def un_processed(error):
    return(
        jsonify({'success': False, 'error': 422,'message': 'your request cannot be processed'}),
        422
    )

# 400 error handler
@app.errorhandler(400)
def bad_request(error):
    return(
        jsonify({'success': False, 'error': 400,'message': 'this is a bad request'}),
        400
    )

# this is 405 error handler
@app.errorhandler(405)
def method_not_allowed(error):
    return(jsonify(
        {
            'success': False,
            'error': 405,
            'message': 'this method is not alllowed'
            }), 405)
