
# PWP SPRING 2023

# DogDict API

![CircleCI](https://dl.circleci.com/status-badge/img/gh/mmouru/pwp-RESTful-api/tree/master.svg?style=shield)

# Group information

* Student 1. Martti Mourujärvi mmouruja19@student.oulu.fi

* Student 2. Kalle Veijalainen kveijala19@student.oulu.fi

* Student 3. Juho Kurula jkurula19@student.oulu.fi

* Student 4. Lauri Suutari lsuutari19@student.oulu.fi

  

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint and instructions on how to setup and run the client__

  

### Flask application usage and database instructions

All dependencies are listed in [requirements.txt](https://github.com/mmouru/pwp-RESTful-api/blob/master/requirements.txt). Database is created with [Flask](https://pypi.org/project/Flask/2.1.3/) (version 2.1.3) and [Flask-SQLAlchemy](https://pypi.org/project/Flask-SQLAlchemy/2.5.1/) (version 2.5.1).

  

To install required external libraries and dependencies, use the following command:

  

```
git clone https://github.com/mmouru/pwp-RESTful-api.git

cd pwp-RESTful-api

pip install -r requirements.txt

```

```
**Warning**
Before using, the application must be either specified as environment variable FLASK_APP or passed in CLI --app flag.
To do this we recommend setting the env variable FLASK_APP to dogdict as (Linux/Mac) export FLASK_APP=dogdict, (Windows CMD) set FLASK_APP=dogdict or (Windows PowerShell) $Env:FLASK_APP = "dogdict". Otherwise specify the --app dogdict in every flask CLI call.
```

  

NOTE: Please make sure you do not already have an existing [test.db](https://github.com/mmouru/pwp-RESTful-api/blob/master/db/instance/test.db) file. It needs to be removed before creating a new one. Otherwise there will be duplication issues.

  

To create and populate the database, use the following command:

```

flask init-db

```

  

After creating the database it can be found in instance folder:

```

cd instance

```

To view the contents of the database, a VSCode extension such as [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer) can be used.

Running the API and UI manually:
(make sure to have set FLASK_APP that was done before, also make sure youre in the root folder)
```
flask --app dogdict run
flask --app dogdict --debug run

python ui.py
```

  

## Testing

  

Models are tested using pytest with coverage reports. 

  

Get coverage % for files these test fill fail if coverage is under 92% in files specified in /.coveragerc

```

coverage run -m pytest

coverage report --fail-under=92

To see missing lines during development
python -m pytest --cov-report term-missing --cov=dogdict tests/

also run pylint to check the code quality, a 9/10 should be reached
pylint dogdict
```

## CircleCI

CircleCI is ran for all branches to ensure that the code is good and app is working, this is checked in two ways:

1. Test coverage for all code is over 92%, this includes new code that is in current commit
2. A container can build from source code indicating that there are no errors in the commit

These tests should be checked during pull request and failures need to be checked and fixed before merging.
CircleCI also releases the containerized app to AWS cloud for further usage if needed.

  

## Running the API with docker

You can build and run the app using docker for easier integration.

Build in root directory where Dockerfile is present

When running you can specify networking inside container so that the app is available in your machine, here port 3000.

```

docker build . --tag dogdict-app

docker run -p 3000:5000 dogdict-app

```
After running the app is available in http://localhost:3000/api/
