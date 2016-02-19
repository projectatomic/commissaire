import requests

from behave import *


@when('we get status')
def impl(context):
    context.request = requests.get(
        context.SERVER + '/api/v0/status', auth=context.auth)


@then('commissaire will return status')
def impl(context):
    results = context.request.json()
    print(results.keys())
    for key in ('investigator', 'etcd', 'clusterexecpool'):
        assert key in results.keys()
