import json
import requests

from behave import *


VALID_USERNAME = 'a'
VALID_PASSWORD = 'a'


def assert_status_code(actual, expected):
    assert actual == expected, \
        'Expected status code {0}, got {1}'.format(expected, actual)


@given('we are anonymous')
def impl(context):
    context.username = None
    context.password = None
    context.auth = (context.username, context.password)


@given('we have a valid username and password')
def impl(context):
    context.username = VALID_USERNAME
    context.password = VALID_PASSWORD
    context.auth = (context.username, context.password)


@then('commissaire will {access} access')
def impl(context, access):
    if access == 'allow':
        assert context.request.status_code != 403
    else:
        assert context.request.status_code == 403


@then('commissaire will note {status}')
def impl(context, status):
    code = None
    if status == 'a bad request':
        code = 400
    elif status == 'it\'s not found':
        code = 404
    elif status == 'a conflict':
        code = 409
    elif status == 'it\'s gone':
        code = 410
    elif status == 'success':
        code = 200
    elif status == 'creation':
        code = 201
    assert_status_code(context.request.status_code, code)


@then('commissaire will provide a {atype}')
def impl(context, atype):
    the_type = None
    if atype == 'list':
        the_type = list
    elif atype == 'dict':
        the_type = dict
    json = context.request.json()
    assert isinstance(json, the_type), \
        'Expected {0} to be a {1}'.format(json, str(the_type))


@then('the provided data is {expected}')
def impl(context, expected):
    json = context.request.json()
    assert json == eval(expected), \
        'Expected {0}, got {1}'.format(expected, json)
