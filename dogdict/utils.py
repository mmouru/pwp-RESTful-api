"""
Some utility functions and converters, also included init-db CLI command for generating db
for development
"""

from werkzeug.exceptions import NotFound, BadRequest
from werkzeug.routing import BaseConverter
import click
from flask.cli import with_appcontext
from dogdict.models import Breed, Facts, Group, Characteristics
from dogdict import db


def breed_name_from_url(url_value):
    """
    Transform two part breed name with underscore to have space inbetween to help db
    search, this does not affect urls with HTML URL encoding like Australian%20Terrier
    """
    breed = url_value
    if "_" in url_value:
        breed = breed.replace("_", " ")
    return breed


def check_for_space(name):
    if " " in name:
        split_by_space = name.split()
        for word in split_by_space:
            if not word.isalpha():
                raise BadRequest(
                f"'{name}' contains unsupported characters. \
                    Only letters and 'space' allowed."
            )
        name = name.replace(" ", "%20")

    return name


class GroupConverter(BaseConverter):
    """
    This can be used to query unique Group information from the database
    """

    def to_python(self, value):
        value = (
            value
        )  # add capitalization so URI does not need to be uppercase
        db_group = Group.query.filter_by(name=value).first()
        if db_group is None:
            raise NotFound(f"Group {value} does not exist")
        return db_group

    def to_url(self, value):
        # THESE NEED TO BE IMPLEMENTED
        print("BREED:", value)
        return str(value)


class BreedConverter(BaseConverter):
    """
    This can be used to query unique Breed information from the database
    """

    def to_python(self, value):
        print(value)
        transformed_name = breed_name_from_url(value)
        db_breed = Breed.query.filter_by(name=transformed_name).first()
        if db_breed is None:
            raise NotFound(f"Breed by name {value} does not exist")
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
            raise NotFound(f"No fact by id {value} found")
        return db_fact

    def to_url(self, value):
        # THESE NEED TO BE IMPLEMENTED
        print("fact:", value)
        return str(value)


@click.command("init-db")
@with_appcontext
def init_db():
    """
    Command line interface to initiliaze a test db to instances/test.db
    """
    db.create_all()
    terriergroup = Group(name="Terrier")
    pastoralgroup = Group(name="Pastoral")
    workinggroup = Group(name="Working")

    # Create a new characteristics
    characteristics_at = Characteristics(life_span=6, coat_length=0.2, exercise=1.2)
    characteristics_asd = Characteristics(life_span=7, coat_length=0.3, exercise=3.3)
    characteristics_am = Characteristics(life_span=8, coat_length=0.4, exercise=3.5)
    characteristics_as = Characteristics(life_span=9, coat_length=0.99, exercise=4.75)

    # Create a new breed and associate it with the group and characteristics
    breed_at = Breed(
        name="Australian Terrier",
        group=terriergroup,
        characteristics=characteristics_at,
    )
    breed_asd = Breed(
        name="Anatolina Shepherd Dog",
        group=pastoralgroup,
        characteristics=characteristics_asd,
    )
    breed_am = Breed(
        name="Alaskan Malamute", group=workinggroup, characteristics=characteristics_am
    )
    breed_as = Breed(
        name="Australian Shepherd",
        group=pastoralgroup,
        characteristics=characteristics_as,
    )

    # Create two facts and associate them with the breed
    fact1 = Facts(fact="Välillä kuin (australian) terrieri...", breed=breed_at)
    fact2 = Facts(fact="They are small dogs", breed=breed_at)

    fact_asd = Facts(
        fact="They have history as livestock guardians and they bark alot",
        breed=breed_asd,
    )
    fact_am = Facts(
        fact="""An immensely strong, heavy-duty worker of spitz type
        , the Alaskan Malamute is an affectionate, loyal, and playful dog""",
        breed=breed_am,
    )

    # Repeat the above for another breed
    breed2 = Breed(
        name="Laurin Terrier", group=terriergroup, characteristics=characteristics_at
    )

    fact3 = Facts(fact="Välillä kuin (australian) terrieri...", breed=breed2)
    fact4 = Facts(fact="They are small dogs", breed=breed2)

    # Commit the changes to the database
    db.session.add(terriergroup)
    db.session.add(pastoralgroup)
    db.session.add(workinggroup)

    db.session.add(characteristics_at)
    db.session.add(characteristics_asd)
    db.session.add(characteristics_am)
    db.session.add(characteristics_as)

    db.session.add(breed_at)
    db.session.add(breed_am)
    db.session.add(breed_as)
    db.session.add(fact1)
    db.session.add(fact2)
    db.session.add(fact_asd)
    db.session.add(fact_am)

    db.session.add(breed2)
    db.session.add(fact3)
    db.session.add(fact4)

    db.session.commit()
