import os
import pytest
import tempfile
import json

from dogdict.models import Group, Facts, Breed
from dogdict import create_app, db


@pytest.fixture
def app():
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_fname)

test_breed_name = "majestic test breed"
group_url = "testgroup"
breed_url = "majestic%20test_breed"

group1 = {
    "name": "test1"
}

group2 = {
    "name": "test2"
}


breed1 = {
    "name": "test_1",
}

breed2 = {
    "asd": "test_2",
}

breed3 = {
    "name": "test_3",
}

def _group(name="testgroup"):
    """
    Init one group to database and return it
    """
    group = Group(
        name=name
    )
    db.session.add(group)
    db.session.commit()
    return group


def _breed(group=False, name=test_breed_name):
    """
    Init one breed to database and return the breed
    """
    
    if group:
        breed = Breed(
            name=name,
            group=_group(),
        )
    else:
        breed = Breed(
            name=name
        )
    db.session.add(breed)
    db.session.commit()
    return breed


def _fact(fact="Fun test fact"):
    """
    Init one fact to database
    """
    breed = _breed(group=True)
    fact = Facts(
        fact=fact,
        breed=breed
    )
    db.session.add(fact)
    db.session.commit()
    return fact


mockFactBody = {
    "breed": test_breed_name,
    "fact": "test fact yay"
}


# Tests for facts

def test_facts_post(app):
    """
    Can post single facts with proper input
    """
    group_url = "testgroup"
    breed_url = "majestic%20test_breed"

    with app.app_context():
        _breed(group=True, name=test_breed_name)
        client = app.test_client()
        res = client.post(f"/api/groups/{group_url}/breeds/{breed_url}/facts/", json=mockFactBody)
        assert res.status_code == 201
        assert Facts.query.count() == 1


def test_facts_get(app):
    """
    GET Facts results in empty array if no facts in db, else return all facts in array
    """
    group_url = "testgroup"
    breed_url = "majestic%20test_breed"
    mock_fact = "Test fact for GET method"
    with app.app_context():
        client = app.test_client()
        _fact(mock_fact)  # init one breed, group and fact to database
        res = client.get(f"/api/groups/{group_url}/breeds/{breed_url}/facts/")
        # decode bytes to string
        data = res.data.decode("utf-8")
        # parse json string
        data = json.loads(data)
        assert data["items"][0]["fact"] == mock_fact

        # returns 404 if cant find singular fact
        res = client.get(f"/api/{group_url}/{breed_url}/facts/400500/")
        assert res.status_code == 404


def test_breeds_post(app):
    """
    POST breeds returns created 201 if valid json body, and returns 400
    if non-existent group is given or otherwise bad body
    """
    with app.app_context():
        client = app.test_client()
        _group() # create one group with name Testgroup

        res = client.post("/api/groups/testgroup/breeds/", json=breed1) # belongs in Testgroup
        assert res.status_code == 201

        res = client.post("/api/groups/testgroup/breeds/", json=breed2) # no name in json body
        assert res.status_code == 400

        res = client.post("/api/groups/non-existent-group/breeds/", json={"name": "mock"})
        assert res.status_code == 404

def test_breeds_get(app):
    """
    GET breeds returns all breeds from database
    """
    with app.app_context():
        client = app.test_client()
        _breed(True)  # init one breed to database
        res = client.get("/api/groups/testgroup/breeds/")
        # decode bytes to string
        data = res.data.decode("utf-8")
        # parse json string
        data = json.loads(data)
        assert len(data["items"]) == 1


def test_post_fact_bad_body(app):
    """
    POST Facts should return BadRequest 400 when bad json body is given in POST request
    method stops in validation
    """
    with app.app_context():
        _breed(group=True) # init breed so the url can be searched
        client = app.test_client()
        bad_body1 = {
            "name2341": "sdfsdf"
        }
        good_body = {"in_breed": "testgroup", "fact": "fact moro"}
        res = client.post(f'/api/groups/{group_url}/breeds/{breed_url}/facts/', json=bad_body1)
        assert res.status_code == 400

        # same fact can not be given twice to breed
        client.post(f'/api/groups/{group_url}/breeds/{breed_url}/facts/', json=good_body)
        res = client.post(f'/api/groups/{group_url}/breeds/{breed_url}/facts/', json=good_body)
        assert res.status_code == 409

        res = client.post(f'/api/groups/non-existent-group/breeds/{breed_url}/facts/', json=good_body)
        assert res.status_code == 404


def test_groups(app):
    """
    First POSTs two groups, then uses GET to make sure there are only two groups
    """
    with app.app_context():
        client = app.test_client()

        res = client.post("/api/groups/", json=group1)
        assert res.status_code == 201

        res = client.post("/api/groups/", json=group2)
        assert res.status_code == 201

        res = client.post("/api/groups/", data=json.dumps(group2))
        assert res.status_code == 415

        res = client.get("/api/groups/")
        data = res.data.decode("utf-8")
        data = json.loads(data)
        assert len(data["items"]) == 2


def test_post_unsupported_media(app):
    """
    If request body is not in correct format, raise UnsupportedMedia error 
    """
    with app.app_context():
        client = app.test_client()
        # init test group and breed to find them
        _breed()
        _group()
        mock_body = {'asd': 'asd', 'perkele': 'perkele'}

        res = client.post(f"/api/groups/{group_url}/breeds/{breed_url}/facts/", data=mock_body)
        assert res.status_code == 415

        res = client.post(f"/api/groups/", data=mock_body)
        assert res.status_code == 415

        res = client.post(f"/api/groups/testgroup/breeds/", data=mock_body)
        assert res.status_code == 415

        res = client.post(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/", data=mock_body)
        assert res.status_code == 415

        _group(name="testgroup123")
        res = client.put("/api/groups/testgroup123/", data=mock_body)
        assert res.status_code == 415


def check_duplicates(app):
    """
    Same named groups and breeds can be created only once
    """
    with app.app_context():
        client = app.test_client()
        _group()
        res = client.post("/api/groups/", json=group1)
        assert res.status_code == 201

        res = client.post("/api/groups/", json=group1)
        assert res.status_code == 409

        res = client.post("/api/breeds/", json=breed1)
        assert res.status_code == 201

        res = client.post("/api/breeds/", json=breed1)
        assert res.status_code == 409


def test_delete(app):
    """
        Creates a fact/breed to make sure there is one in the database, then
        deletes it and makes sure it is deleted (status code 204).
        If it doesnt exist returns 404.
    """
    with app.app_context():
        client = app.test_client()
        _breed()  # init one breed to database
        _group()  # init one group to database
        res = client.post(f"/api/groups/{group_url}/breeds/{breed_url}/facts/", json=mockFactBody)
        assert res.status_code == 201

        res = client.delete(f"/api/groups/{group_url}/breeds/{breed_url}/facts/1/")
        assert res.status_code == 204

        # fails if fact not found
        res = client.delete(f"/api/groups/{group_url}/breeds/{breed_url}/facts/1500606969696969/")
        assert res.status_code == 404

def test_characteristics_post(app):
    """
    POST request for characteristics fails if breed is not database
    """
    bad_body ={
        "life_span": 6,
        "in_breed": "non existing breed"
    }
    with app.app_context():
        client = app.test_client()
        _group() # init the group
        res = client.post(f"/api/groups/{group_url}/breeds/non-existing-breed/characteristics/", json=bad_body)
        assert res.status_code == 404

        # returns 400 if post validation fails
        res = client.post(f"/api/groups/{group_url}/breeds/non-existing-breed/characteristics/", json={"martti": "badbad"})
        assert res.status_code == 400

def test_characteristics_get_and_put_methods(app):
    """
    GET characteristics should return correct response
    """
    with app.app_context():
        client = app.test_client()
        _breed(group=True)
        chars = {
            "in_breed": test_breed_name,
            "life_span": 7
        }
        # test that characteristics can be added if not exist in breed
        res = client.post(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/", json=chars)
        assert res.status_code == 201

        # test that characteristics raise integrity error if already exist
        res = client.post(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/", json=chars)
        assert res.status_code == 409

        # test posting characteristic to existing breed
        # we get the characteristics as response from get
        res = client.get(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/")
        assert res.status_code == 200
        data = res.data.decode("utf-8")
        data = json.loads(data)
        assert data["items"][0] == {'@controls': {'self': {'href': '/api/groups/testgroup/breeds/majestic%20test%20breed/characteristics/'}}, 'coat_length': None, 'exercise': None, 'life_span': 7}

        # returns 204 when characteristics is good
        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/", json={"life_span": 13, "coat_length": 0.8, "exercise": 4})
        assert res.status_code == 204

        # returns 415 for put if body is not in json
        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/", data="WRONG MEDIA TYPE")
        assert res.status_code == 415

        # return 404 if put schema validation fails
        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/characteristics/", json={"martti": "joujou"})
        assert res.status_code == 400

def test_characteristics_post(app):
    """
    Existing breed can be given a characteristic, with different combinations

    """ 
    with app.app_context():
        client = app.test_client()
        breed = _breed(group=True,name="first good boy")

        good_body = {
            "life_span": 6, # Not nullable
            "in_breed": breed.name
            }

        res = client.post(f"/api/groups/{group_url}/breeds/first_good_boy/characteristics/", json=good_body)
        assert res.status_code == 201

def test_characteristics_post_exercise(app):
    """
        POST request for characteristics is possible with defined exercise value
    """
    with app.app_context():
        client = app.test_client()
        breed = _breed(group=True,name="first good boy")

        good_body = {
            "life_span": 6, # Not nullable
            "in_breed": breed.name,
            "exercise": 4
            }

        res = client.post(f"/api/groups/{group_url}/breeds/first_good_boy/characteristics/", json=good_body)
        assert res.status_code == 201

def test_characteristics_post_exercise_and_coatlength(app):
    """
        POST request for characteristics is possible with defined exercise and coat length values
    """
    with app.app_context():
        client = app.test_client()
        breed = _breed(group=True, name="first good boy")

        good_body = {
            "life_span": 6, # Not nullable
            "in_breed": breed.name,
            "exercise": 4,
            "coat_length": 1
            }

        res = client.post(f"/api/groups/{group_url}/breeds/first_good_boy/characteristics/", json=good_body)
        assert res.status_code == 201

def test_notfound(app):
    """
        Tests if not found error is correctly outputted for breed and group.
        For formatters.
    """
    with app.app_context():
        _group()
        client = app.test_client()
        res = client.get(f"/api/groups/testgroup/breeds/PerkeleenKoira/")
        assert res.status_code == 404

        res = client.get(f"/api/groups/PerkeleenTerrier/")
        assert res.status_code == 404


def test_put_group(app):
    """
        Group PUT requests return correct responses for valid and invalid bodies
    """
    with app.app_context():
        client = app.test_client()
        res = client.post("/api/groups/", json=group1)
        assert res.status_code == 201
        group_name = group1["name"]
        res = client.put(f"/api/groups/{group_name}/", json=group2)
        assert res.status_code == 204

def test_group_validation(app):
    """
    Test that group return bad request 400 with invalid json
    """

    body = {
        "group_name": "value does not exist"
    }
    with app.app_context():
        client = app.test_client()

        res = client.post("/api/groups/", json=body)
        assert res.status_code == 400

def test_group_already_exists(app):
    """
    Returns conflict 409 if named group already exists in db
    """
    group_name = "Fun test group yeah!"

    body = {
        "name": group_name
    }
    with app.app_context():
        client = app.test_client()
        _group(name=group_name)
        res = client.post("/api/groups/", json=body)
        assert res.status_code == 409

def test_breed_already_exists(app):
    """
    Return 409 if named breed already exists in db
    """
    breed_name = "Haha Fun Breed L0L"

    body = {
        "name": breed_name,
        "group": "Testgroup"
    }
    with app.app_context():
        client = app.test_client()
        _breed(name=breed_name, group=True)

        res = client.post(f"/api/groups/testgroup/breeds/", json=body)
        assert res.status_code == 409

def test_post_fact_breed_exists(app):
    """
    Return 404 if breed does not exist in database when giving a fact
    """
    breed_name = "non_existing"
    with app.app_context():
        _group(name="mockgroup") # group named Testgroup exists
        client = app.test_client()
        res = client.post(f"/api/groups/mockgroup/breeds/{breed_name}/facts/", json={"fact": "mock fact", "breed": breed_name})
        assert res.status_code == 404

def test_post_characteristics_duplicate(app):
    """
    Test that POSTs characteristics twice to a breed, resulting in error 409 (1 to 1 relationship)
    """
    breed_name = "fun fun breed name"
    body = {
    "in_breed": breed_name,
    "char_id": 1,
    "coat_length": 0.2,
    "life_span": 6,
    "exercise": 1.2
    }
    with app.app_context():
        client = app.test_client()
        _breed(group=True, name="fun fun breed name")
        res = client.post(f"/api/groups/{group_url}/breeds/fun%20fun%20breed%20name/characteristics/", json=body)
        assert res.status_code == 201
        res = client.post(f"/api/groups/{group_url}/breeds/fun%20fun%20breed%20name/characteristics/", json=body)
        assert res.status_code == 409
        

def test_group_item_get(app):
    """
    Test that singular group can be found with url, and the uri does not need capitalized group
    """
    with app.app_context():
        client = app.test_client()
        _group(name="marttionparas")

        res = client.get("/api/groups/marttionparas/")
        data = res.data.decode("utf-8")
        print(res)
        data = json.loads(data)
        print(data["items"])
        assert data["items"] == [{'name': 'marttionparas', 'breeds': []}]
    
def test_group_put_validation(app):
    """
    Returns 400 bad request if body does not conform to group schema
    """
    with app.app_context():
        client = app.test_client()
        _group(name="testgroup123")
        res = client.put("/api/groups/testgroup123/", json={"not_valid": "attribute"})
        assert res.status_code == 400

def test_get_breed(app):
    """
    Test that return breed can be found with breed name, does not need to be capitalized
    in url
    """
    with app.app_context():
        client = app.test_client()
        _breed(group=True)

        res = client.get(f"/api/groups/{group_url}/breeds/{breed_url}/") 
        data = res.data.decode("utf-8")
        data = json.loads(data)
        print(data)
        assert data == {'items': [{'name': 'majestic test breed', 'id': 1, 'group': {'name': 'testgroup', 'id': 1}, 'facts': [], '@controls': {'self': {'href': '/api/groups/testgroup/breeds/majestic%20test%20breed/'}}}], '@namespaces': {'breeds': {'name': '/api/groups/testgroup/breeds/majestic%20test%20breed/'}}, '@controls': {'self': {'href': '/api/groups/testgroup/breeds/majestic%20test%20breed/'}, 'edit': {'method': 'PUT', 'encoding': 'json', 'title': 'breed:edit', 'schema': {'type': 'object', 'required': ['name'], 'properties': {'name': {'description': 'Breeds unique name', 'type': 'string'}}}, 'href': '/api/groups/testgroup/breeds/majestic%20test%20breed/'}, 'breed:delete': {'method': 'DELETE', 'href': '/api/groups/testgroup/breeds/majestic%20test%20breed/'}}}

def test_put_breed(app):
    """
    Test that breeds name and group can be changed
    """
    # Validation by Breed validator so group is needed, maybe other validator here    
    body = {
        "name": "testbreed200003000",
        "group": "Changegroup"
    }
    with app.app_context():
        client = app.test_client()
        _breed(group=True)

        _group(name="Changegroup") # we change group to this

        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/", json=body)
        assert res.status_code == 204

def test_breed_put_validation(app):
    """
    PUT method should return 400 for bad body
    """
    body = {
        "martti": "hajottaa"
    }
    with app.app_context():
        client = app.test_client()
        _breed(group=True)
    
        res = client.put(f"api/groups/{group_url}/breeds/{breed_url}/", json=body)
        assert res.status_code == 400

def test_fact_item_put(app):
    """
    PUT should return something something
    """
    with app.app_context():
        client = app.test_client()
        _fact() # init fact, group, breed all at once

        # returns 415 for unsupported media
        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/facts/1/", data="not json")
        assert res.status_code == 415
        
        # validation returns 409 if no fact in json
        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/facts/1/", json={"martti": "mouru"})
        assert res.status_code == 400

        res = client.put(f"/api/groups/{group_url}/breeds/{breed_url}/facts/1/", json={"fact": "changed fact about doggo"})
        assert res.status_code == 204

def test_fact_item_get(app):
    """
    GEt method returns correct responses
    """

    with app.app_context():
        client = app.test_client()
        _fact() # init fact, group, breed all at once

        res = client.get(f"/api/groups/{group_url}/breeds/{breed_url}/facts/1/")
        assert res.status_code == 200

def test_breed_delete(app):
    """
    DELETE breed returns 204 if succesful and 404 if unsuccesful
    """
    
    with app.app_context():
        client = app.test_client()
        _breed(group=True)
        # returns 404 for non existing breed
        res = client.delete(f"/api/groups/{group_url}/breeds/{breed_url}202020/")
        assert res.status_code == 404
        # returns 204 for found breed and deletes it
        res = client.delete(f"/api/groups/{group_url}/breeds/{breed_url}/")
        assert res.status_code == 204
    