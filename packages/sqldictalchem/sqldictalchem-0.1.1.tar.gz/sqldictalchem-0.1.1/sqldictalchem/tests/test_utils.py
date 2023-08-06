# vim: set fileencoding=utf-8 :


import unittest
import sqldictalchem.tests as tests
from sqldictalchem import make_class_dictable
from sqldictalchemy import create_engine
from sqldictalchemy.orm import sessionmaker
from sqldictalchemy import Column, String, Integer

engine = create_engine('sqlite:///:memory:', echo=False)
from sqldictalchemy.ext.declarative import declarative_base
Base = declarative_base(engine)


class MakeClassDictable(Base):

    __tablename__ = 'makeclassdictable'

    id = Column(Integer, primary_key=True)

    name = Column(String)

    def __init__(self, name):
        self.name = name


class TestAsdict(unittest.TestCase):

    def setUp(self):
        """ Recreate the database """
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def tearDown(self):
        Base.metadata.drop_all()

    def test_make_class_dictable(self):
        assert not hasattr(MakeClassDictable, 'asdict')
        m = MakeClassDictable('dictable')
        self.session.add(m)
        self.session.commit()

        assert not hasattr(m, 'asdict')
        make_class_dictable(MakeClassDictable)
        assert m.asdict() == {'id': m.id, 'name': m.name}


class TestMakeDictable(tests.TestCase):

    def test_dict(self):
        named = tests.Named('a name')
        self.session.add(named)
        self.session.commit()
        assert dict(named) == {'id': named.id, 'name': 'a name'}


def test_arg_to_dict():

    from sqldictalchem.utils import arg_to_dict

    assert arg_to_dict(None) == {}
    assert arg_to_dict([]) == {}
    assert arg_to_dict(['a', 'b']) == {'a': {}, 'b': {}}
    assert arg_to_dict({
        'a': {'is_a': True},
        'b': {'is_b': True},
    }) == {'a': {'is_a': True}, 'b': {'is_b': True}}
