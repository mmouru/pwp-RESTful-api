"""
    Contains all the resources that are used to access the Facts model in the database.
"""

import json
from jsonschema import validate, ValidationError
from flask import Response, request, url_for
from werkzeug.exceptions import Conflict, BadRequest, UnsupportedMediaType
from sqlalchemy.exc import IntegrityError
from flask_restful import Resource
from dogdict.models import Group, Breed, db
from dogdict.constants import JSON


class GroupCollection(Resource):
    """
        Used to access all of the Groups in the DB at once.
    """
    def get(self):
        """
            GETs all the groups in the database (currently their names)
        """
        body = {"items": []}
        for db_group in Group.query.all():
            item = db_group.serialize(short_form=False)
            body["items"].append(item)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def post(self):
        """
            Used to POST a new Group object and validate it against the Group
            JSON schema.
        """
        if not request.is_json:
            raise UnsupportedMediaType

        try:
            validate(request.json, Group.json_schema())
        except ValidationError as exc:
            raise BadRequest(description=str(exc))

        group = Group(name=request.json["name"])

        try:
            db.session.add(group)
            db.session.commit()
        except IntegrityError:
            raise Conflict(
                f"Group with name '{request.json['name']}' already exists."
            )

        return Response(
            status=201, headers={"Item": url_for("api.groupcollection", group=group)}
        )


class GroupItem(Resource):
    """
        Used to access a specific group
    """
    def get(self, group):
        """
            GETs a specific groups information from the DB (name only)
        """
        
        body = {
            "group": group.name,
            "breeds": []
            }
        # Get all breeds that are under group
        for breed in Breed.query.filter_by(group=group).all():
            body["breeds"].append(breed.name)

        return Response(json.dumps(body), 200, mimetype=JSON)

    def put(self, group):
        """
            Used to change the name of a specific group from the database.
        """
        if not request.is_json:
            return "Unsupported Media Type!", 415
        try:
            validate(request.json, Group.json_schema())

        except ValidationError as exc:
            raise BadRequest(description=str(exc)) from exc

        group.deserialize(request.json)

        db.session.add(group)
        db.session.commit()

        return Response(status=204)
