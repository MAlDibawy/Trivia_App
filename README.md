# trivia API

Trivia api is a web app that allows to hold trivia questions and manage to play the game.

The app allows the user to:

1) Display questions. 
2) Delete questions.
3) Add questions and their answers.
4) Search for questions based on substrings.
5) Play the quiz game.

## Getting started

## Installing Dependencies

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment
Working within a virtual environment is recommended.

#### PIP Dependencies

navigate to `/backend` directory and run:

```bash
pip install -r requirements.txt
```

This will install all of the required packages in the `requirements.txt` file.

#### key dependencies

- FLASK
- SQLAlchemy
- Flask-CORS

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. Navigate to `/backend` directory and run:

```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```


## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

#### Frontend Dependencies

This project uses NPM to manage software dependencies. from the `frontend` directory run:

```bash
npm install
```

## Authors
- Mahmoud AlDibawy worked on the API to integrate with the frontend
- Udacity provided the starter files for the project including the frontend
