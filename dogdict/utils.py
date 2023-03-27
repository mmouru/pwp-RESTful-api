from flask import Response
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter
from dogdict.models import Breed, Facts, Group


def breed_name_from_url(url_value):
    """
        Transform two part breed name with underscore to have space inbetween to help db 
        search, this does not affect urls with HTML URL encoding like Australian%20Terrier
    """
    breed = url_value
    if "_" in url_value:
        breed = breed.replace("_", " ")
    return breed.title() # title capitalizes all words

class GroupConverter(BaseConverter):
    """
        This can be used to query unique Group information from the database
    """
    def to_python(self, value):
        value = value.capitalize()  # add capitalization so URI does not need to be uppercase
        db_group = Group.query.filter_by(name=value).first()
        if db_group is None:
            raise NotFound
        return db_group

    def to_url(self, value):
        # THESE NEED TO BE IMPLEMENTED
        print("BREED:", value)
        return str(value)


class BreedConverter(BaseConverter):
    """
        This can be used to query unique Breed information from the database
    """
    def to_python(self, value):  # MARTTI MUUTTI TÄMÄN ID:LLÄ TOIMIVAKSI, MIETITÄÄN MITÄ TAPAHTUU
        transformed_name = breed_name_from_url(value)
        db_breed = Breed.query.filter_by(name=transformed_name).first()
        if db_breed is None:
            return Response(status=404)
        return db_breed

    def to_url(self, value):
        # THESE NEED TO BE IMPLEMENTED
        print("BREED:", value)
        return str(value)


class FactConverter(BaseConverter):
    """
        This can be used to query unique Fact information from the database
        Searched by id of fact
    """
    def to_python(self, value):
        db_fact = Facts.query.filter_by(id=value).first()
        if db_fact is None:
            return None
        return db_fact

    def to_url(self, value):
        # THESE NEED TO BE IMPLEMENTED
        print("fact:", value)
        return str(value)
