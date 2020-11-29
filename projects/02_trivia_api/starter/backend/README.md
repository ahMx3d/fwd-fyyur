# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

REVIEW_COMMENT
```
The Endpoints Documentations:

Endpoints
GET '/categories'
GET '/questions'
DELETE '/questions/<question_id>'
POST '/questions'
GET '/categories/<category_id>/questions'
POST '/quizzes'

GET '/categories'
- Handles GET requests for all available categories.
- Request Arguments: None
- Returns a dictionary of each category's id and type in the format of key: value pairs.
- Response:
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "message": "Categories retrieved successfully",
    "status" : 200,
    "success": true
}

GET '/questions'
- Handles GET requests for questions including pagination (every 10 questions).
- Request Arguments: None
- Returns list of questions, number of total questions, current category, categories.
- Response:
{
    "categories": {
        "1": "Science",
        "2": "Art",
        "3": "Geography",
        "4": "History",
        "5": "Entertainment",
        "6": "Sports"
    },
    "current_category": null,
    "message"         : "Categories & questions retrieved successfully",
    "questions"       : [
        {
            "answer"    : "this is the new test question",
            "category"  : 2,
            "difficulty": 4,
            "id"        : 33,
            "question"  : "what is the new test question?"
        },
        {
            "answer"    : "this is the new question",
            "category"  : 5,
            "difficulty": 1,
            "id"        : 32,
            "question"  : "what is the new question?"
        },
        {
            "answer"    : "OK here we go",
            "category"  : 2,
            "difficulty": 2,
            "id"        : 31,
            "question"  : "fdsfds"
        },
        {
            "answer"    : "OK here we go",
            "category"  : 2,
            "difficulty": 3,
            "id"        : 29,
            "question"  : "what about another try?"
        },
        {
            "answer"    : "u will do it",
            "category"  : 5,
            "difficulty": 1,
            "id"        : 28,
            "question"  : "what do u think?"
        },
        {
            "answer"    : "Scarab",
            "category"  : 4,
            "difficulty": 4,
            "id"        : 23,
            "question"  : "Which dung beetle was worshipped by the ancient Egyptians?"
        },
        {
            "answer"    : "Blood",
            "category"  : 1,
            "difficulty": 4,
            "id"        : 22,
            "question"  : "Hematology is a branch of medicine involving the study of what?"
        },
        {
            "answer"    : "Alexander Fleming",
            "category"  : 1,
            "difficulty": 3,
            "id"        : 21,
            "question"  : "Who discovered penicillin?"
        },
        {
            "answer"    : "The Liver",
            "category"  : 1,
            "difficulty": 4,
            "id"        : 20,
            "question"  : "What is the heaviest organ in the human body?"
        },
        {
            "answer"    : "Jackson Pollock",
            "category"  : 2,
            "difficulty": 2,
            "id"        : 19,
            "question"  : "Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"
        }
    ],
    "status"         : 200,
    "success"        : true,
    "total_questions": 23
}

DELETE '/questions/<question_id>'
- Handles DELETE question using a question ID.
- Request Arguments: question_id
- Response:
{
    "message": "The question deleted successfully",
    "status" : 200,
    "success": true
}

POST '/questions'
- Handles get questions based on a search term.
- Returns any questions for whom the search term is a substring of the question.
- Response:
{
    'success'        : true,
    'status'         : 200,
    'questions'      : [
        {
            "answer"    : "OK here we go",
            "category"  : 2,
            "difficulty": 2,
            "id"        : 31,
            "question"  : "fdsfds"
        }
    ],
    "total_questions": 1,
    'message'        : 'the questions searched found successfully'
}

- Handles POST a new question, which will require the question and answer text, category, and difficulty score.
- Returns the newly created question id.
- Request Arguments: None
- Response:
{
    'success': true,
    'status' : 201,
    'created': 50,
    'message': 'The question created successfully'
}

GET '/categories/<category_id>/questions'
- Handles a GET request to get questions based on category, and 
- Returns list of all paginated questions for each page.
- Request Arguments: category_id
- Response:
{
    "current_category": 5,
    "message"         : "the questions of category \"Entertainment\" found successfully",
    "questions"       : [
        {
            "answer"    : "this is the new question",
            "category"  : 5,
            "difficulty": 1,
            "id"        : 32,
            "question"  : "what is the new question?"
        },
        {
            "answer"    : "Edward Scissorhands",
            "category"  : 5,
            "difficulty": 3,
            "id"        : 6,
            "question"  : "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
        },
        {
            "answer"    : "Tom Cruise",
            "category"  : 5,
            "difficulty": 4,
            "id"        : 4,
            "question"  : "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
        }
    ],
    "status"         : 200,
    "success"        : true,
    "total_questions": 3
}

POST '/quizzes'
- Handles a POST request to get questions to play the quiz. This endpoint takes category and previous question parameters.
- Return a random questions within the given category, if provided, and that is not one of the previous questions.
- Response:
{
    "success"         : true,
    "status"          : 200,
    "question"        : {
        "answer"    : "Edward Scissorhands",
        "category"  : 5,
        "difficulty": 3,
        "id"        : 6,
        "question"  : "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
}

The server handled error types:

400 - Bad Request
{
    'success': False,
    'error':400,
    'message':'Bad Request'
}

404 - Resource not Found
{
    'success': False,
    'error':404,
    'message':'Resource not Found'
}

405 - Method not Allowed
{
    'success': False,
    'error':405,
    'message':'Method not Allowed'
}

422 - Unprocessable Entity
{
    'success': False,
    'error':422,
    'message':'Unprocessable Entity'
}

500 - Internal Server Error
{
    'success': False,
    'error':500,
    'message':'Internal Server Error'
}
```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```