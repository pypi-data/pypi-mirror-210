# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring


from pymvola.util.authorization import basic_authorization


def test_generation_of_basic_authorization_string():
    login = "username"
    passwd = "password"
    basic_authorization_str = basic_authorization(login, passwd)

    assert basic_authorization_str == "Basic dXNlcm5hbWU6cGFzc3dvcmQ="
