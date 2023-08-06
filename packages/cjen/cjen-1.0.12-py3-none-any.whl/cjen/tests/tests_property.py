import pytest

from cjen.exceptions import PropertyRequiredException, PropertyRangerException, RequestParamErr
from cjen.nene.properties import required, required_if, should_be_in


class TestObj:
    def __init__(self, data: dict):
        self.data = data

    @property
    @required()
    def name(self): return self.data.get("name")

    @property
    @required_if(proper="name", wish=["jia"])
    def nick_name(self): return self.data.get("nick_name")

    @property
    @should_be_in(limits=["a", "b", "c"])
    def email(self): return "a"

    @property
    @should_be_in(limits=["a", "b", "c"])
    def invalid_email(self): return "A"

    @property
    @should_be_in(limits=["a", "b", "c"], ignore_case=True)
    def ignore_case_email(self): return "A"

    @property
    @required(exception_class=RequestParamErr, err_msg="test")
    def sid(self):
        return None

    @property
    @required_if(proper="name", wish=["jia"], exception_class=RequestParamErr, err_msg="test")
    def fly(self): return None

    @property
    @should_be_in(limits=["a", "b", "c"], ignore_case=True, exception_class=RequestParamErr, err_msg="test")
    def tree(self): return 'd'


def test_required():
    obj = TestObj(dict(name="1"))
    assert obj.name == "1"


def test_required_exception():
    obj = TestObj(dict(name1="1"))
    with pytest.raises(PropertyRequiredException, match='name 必填'):
        obj.name


def test_required_if():
    obj = TestObj(dict(name="1", nick_name='3'))
    assert obj.nick_name == '3'

    obj = TestObj(dict(name="1"))
    assert obj.nick_name is None


def test_required_if_exception():
    obj = TestObj(dict(name="jia"))
    with pytest.raises(PropertyRequiredException, match='nick_name 必填'):
        obj.nick_name


def test_email():
    obj = TestObj(dict(name="jia"))
    assert obj.email == "a"


def test_invalid_email():
    obj = TestObj(dict(name="jia"))
    with pytest.raises(PropertyRangerException):
        obj.invalid_email


def test_ignore_case_email():
    obj = TestObj(dict(name="jia"))
    assert obj.ignore_case_email == 'A'


def test_custom_invalid():
    obj = TestObj(dict(name="jia"))
    with pytest.raises(RequestParamErr):
        obj.sid

    with pytest.raises(RequestParamErr):
        obj.fly
    with pytest.raises(RequestParamErr):
        obj.tree