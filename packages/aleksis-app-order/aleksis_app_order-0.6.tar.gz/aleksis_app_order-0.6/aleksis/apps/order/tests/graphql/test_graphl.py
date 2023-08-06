import json

import pytest
from graphene_django.utils.testing import graphql_query

from aleksis.apps.order.models import OrderForm


@pytest.fixture
def graphql_user(django_user_model):
    username = "foo"
    password = "bar"

    if not django_user_model.objects.filter(username=username).exists():
        django_user_model.objects.create_user(username=username, password=password)
    return django_user_model.objects.get(username=username)


@pytest.fixture
def client_query(client, graphql_user):
    client.login(username=graphql_user.username, password="bar")

    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client)

    return func


@pytest.fixture
def order_form():
    return OrderForm.objects.create(
        title="Test Order Form",
        access_code="secret_code",
        from_name="Test From",
        from_email="test@example.com",
    )


@pytest.fixture
def order_form_public(order_form):
    order_form.access_code = ""
    order_form.save()
    return order_form


def test_order_form_by_id_secured_without_login_without_access_code(client_query, order_form):
    response = client_query(
        """
        query($id: Int!) {
            orderFormById(id: $id) {
                title
            }
        }
        """,
        variables={"id": order_form.id},
    )
    print(response.content)
    content = json.loads(response.content)
    print(content)
    assert content["data"]["orderFormById"]["name"] == "Test Order Form"


def test_order_form_by_id_secured_without_login_with_access_code(client_query, order_form):
    response = client_query(
        """
        query($id: Int!) {
            orderFormById(id: $id, accessCode: "secret_code") {
                title
            }
        }
        """,
        variables={"id": order_form.id},
    )
    print(response.content)
    content = json.loads(response.content)
    print(content)
    assert not content["data"]["orderFormById"]


# def test_order_form_by_id_secured_with_login_without_access_code(client_query, order_form):
