# -*- coding: utf-8 -*-
import json

import pytest
from apistar.exceptions import ErrorResponse

from arkindex.mock import MockApiClient
from arkindex_worker.cache import CachedElement
from arkindex_worker.models import Element
from arkindex_worker.worker import MetaType

from . import BASE_API_CALLS


def test_create_metadata_wrong_element(mock_elements_worker):
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=None,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be of type Element or CachedElement"
    )

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element="not element type",
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be of type Element or CachedElement"
    )


def test_create_metadata_wrong_type(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=None,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=1234,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type="not_a_metadata_type",
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"


def test_create_metadata_wrong_name(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name=None,
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name=1234,
            value="La Turbine, Grenoble 38000",
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"


def test_create_metadata_wrong_value(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value=None,
        )
    assert str(e.value) == "value shouldn't be null and should be of type str"

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value=1234,
        )
    assert str(e.value) == "value shouldn't be null and should be of type str"


def test_create_metadata_wrong_entity(mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})

    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
            entity=1234,
        )
    assert str(e.value) == "entity should be of type str"


def test_create_metadata_api_error(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_metadata(
            element=elt,
            type=MetaType.Location,
            name="Teklia",
            value="La Turbine, Grenoble 38000",
        )

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]


def test_create_metadata(responses, mock_elements_worker):
    elt = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    metadata_id = mock_elements_worker.create_metadata(
        element=elt,
        type=MetaType.Location,
        name="Teklia",
        value="La Turbine, Grenoble 38000",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "location",
        "name": "Teklia",
        "value": "La Turbine, Grenoble 38000",
        "entity_id": None,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert metadata_id == "12345678-1234-1234-1234-123456789123"


def test_create_metadata_cached_element(responses, mock_elements_worker_with_cache):
    elt = CachedElement.create(id="12341234-1234-1234-1234-123412341234", type="thing")
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        status=200,
        json={"id": "12345678-1234-1234-1234-123456789123"},
    )

    metadata_id = mock_elements_worker_with_cache.create_metadata(
        element=elt,
        type=MetaType.Location,
        name="Teklia",
        value="La Turbine, Grenoble 38000",
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body) == {
        "type": "location",
        "name": "Teklia",
        "value": "La Turbine, Grenoble 38000",
        "entity_id": None,
        "worker_run_id": "56785678-5678-5678-5678-567856785678",
    }
    assert metadata_id == "12345678-1234-1234-1234-123456789123"


@pytest.mark.parametrize(
    "metadatas",
    [
        ([{"type": MetaType.Text, "name": "fake_name", "value": "fake_value"}]),
        (
            [
                {
                    "type": MetaType.Text,
                    "name": "fake_name",
                    "value": "fake_value",
                    "entity_id": "fake_entity_id",
                }
            ]
        ),
    ],
)
def test_create_metadatas(responses, mock_elements_worker, metadatas):
    element = Element({"id": "12341234-1234-1234-1234-123412341234"})
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        status=201,
        json={
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "metadata_list": [
                {
                    "id": "fake_metadata_id",
                    "type": metadatas[0]["type"].value,
                    "name": metadatas[0]["name"],
                    "value": metadatas[0]["value"],
                    "dates": [],
                    "entity_id": metadatas[0].get("entity_id"),
                }
            ],
        },
    )

    created_metadatas = mock_elements_worker.create_metadatas(element, metadatas)

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body)["metadata_list"] == [
        {
            "type": metadatas[0]["type"].value,
            "name": metadatas[0]["name"],
            "value": metadatas[0]["value"],
            "entity_id": metadatas[0].get("entity_id"),
        }
    ]
    assert created_metadatas == [
        {
            "id": "fake_metadata_id",
            "type": metadatas[0]["type"].value,
            "name": metadatas[0]["name"],
            "value": metadatas[0]["value"],
            "dates": [],
            "entity_id": metadatas[0].get("entity_id"),
        }
    ]


@pytest.mark.parametrize(
    "metadatas",
    [
        ([{"type": MetaType.Text, "name": "fake_name", "value": "fake_value"}]),
        (
            [
                {
                    "type": MetaType.Text,
                    "name": "fake_name",
                    "value": "fake_value",
                    "entity_id": "fake_entity_id",
                }
            ]
        ),
    ],
)
def test_create_metadatas_cached_element(
    responses, mock_elements_worker_with_cache, metadatas
):
    element = CachedElement.create(
        id="12341234-1234-1234-1234-123412341234", type="thing"
    )
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        status=201,
        json={
            "worker_run_id": "56785678-5678-5678-5678-567856785678",
            "metadata_list": [
                {
                    "id": "fake_metadata_id",
                    "type": metadatas[0]["type"].value,
                    "name": metadatas[0]["name"],
                    "value": metadatas[0]["value"],
                    "dates": [],
                    "entity_id": metadatas[0].get("entity_id"),
                }
            ],
        },
    )

    created_metadatas = mock_elements_worker_with_cache.create_metadatas(
        element, metadatas
    )

    assert len(responses.calls) == len(BASE_API_CALLS) + 1
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
    ]
    assert json.loads(responses.calls[-1].request.body)["metadata_list"] == [
        {
            "type": metadatas[0]["type"].value,
            "name": metadatas[0]["name"],
            "value": metadatas[0]["value"],
            "entity_id": metadatas[0].get("entity_id"),
        }
    ]
    assert created_metadatas == [
        {
            "id": "fake_metadata_id",
            "type": metadatas[0]["type"].value,
            "name": metadatas[0]["name"],
            "value": metadatas[0]["value"],
            "dates": [],
            "entity_id": metadatas[0].get("entity_id"),
        }
    ]


@pytest.mark.parametrize(
    "wrong_element",
    [
        None,
        "not_element_type",
        1234,
        12.5,
    ],
)
def test_create_metadatas_wrong_element(mock_elements_worker, wrong_element):
    wrong_metadatas = [
        {"type": MetaType.Text, "name": "fake_name", "value": "fake_value"}
    ]
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadatas(
            element=wrong_element, metadatas=wrong_metadatas
        )
    assert (
        str(e.value)
        == "element shouldn't be null and should be of type Element or CachedElement"
    )


@pytest.mark.parametrize(
    "wrong_type",
    [
        None,
        "not_metadata_type",
        1234,
        12.5,
    ],
)
def test_create_metadatas_wrong_type(mock_elements_worker, wrong_type):
    element = Element({"id": "12341234-1234-1234-1234-123412341234"})
    wrong_metadatas = [{"type": wrong_type, "name": "fake_name", "value": "fake_value"}]
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadatas(
            element=element, metadatas=wrong_metadatas
        )
    assert str(e.value) == "type shouldn't be null and should be of type MetaType"


@pytest.mark.parametrize("wrong_name", [(None), (1234), (12.5), ([1, 2, 3, 4])])
def test_create_metadatas_wrong_name(mock_elements_worker, wrong_name):
    element = Element({"id": "fake_element_id"})
    wrong_metadatas = [
        {"type": MetaType.Text, "name": wrong_name, "value": "fake_value"}
    ]
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadatas(
            element=element, metadatas=wrong_metadatas
        )
    assert str(e.value) == "name shouldn't be null and should be of type str"


@pytest.mark.parametrize("wrong_value", [(None), ([1, 2, 3, 4])])
def test_create_metadatas_wrong_value(mock_elements_worker, wrong_value):
    element = Element({"id": "fake_element_id"})
    wrong_metadatas = [
        {"type": MetaType.Text, "name": "fake_name", "value": wrong_value}
    ]
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadatas(
            element=element, metadatas=wrong_metadatas
        )
    assert (
        str(e.value)
        == "value shouldn't be null and should be of type (str or float or int)"
    )


@pytest.mark.parametrize(
    "wrong_entity",
    [
        [1, 2, 3, 4],
        1234,
        12.5,
    ],
)
def test_create_metadatas_wrong_entity(mock_elements_worker, wrong_entity):
    element = Element({"id": "fake_element_id"})
    wrong_metadatas = [
        {
            "type": MetaType.Text,
            "name": "fake_name",
            "value": "fake_value",
            "entity_id": wrong_entity,
        }
    ]
    with pytest.raises(AssertionError) as e:
        mock_elements_worker.create_metadatas(
            element=element, metadatas=wrong_metadatas
        )
    assert str(e.value) == "entity_id should be None or a str"


def test_create_metadatas_api_error(responses, mock_elements_worker):
    element = Element({"id": "12341234-1234-1234-1234-123412341234"})
    metadatas = [
        {
            "type": MetaType.Text,
            "name": "fake_name",
            "value": "fake_value",
            "entity_id": "fake_entity_id",
        }
    ]
    responses.add(
        responses.POST,
        "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        status=500,
    )

    with pytest.raises(ErrorResponse):
        mock_elements_worker.create_metadatas(element, metadatas)

    assert len(responses.calls) == len(BASE_API_CALLS) + 5
    assert [
        (call.request.method, call.request.url) for call in responses.calls
    ] == BASE_API_CALLS + [
        # We retry 5 times the API call
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
        (
            "POST",
            "http://testserver/api/v1/element/12341234-1234-1234-1234-123412341234/metadata/bulk/",
        ),
    ]


def test_list_element_metadata(fake_dummy_worker):
    element = Element({"id": "element_id"})
    fake_dummy_worker.api_client.add_response(
        "ListElementMetaData",
        id=element.id,
        response={"id": "metadata_id"},
    )
    assert fake_dummy_worker.list_element_metadata(element) == {"id": "metadata_id"}

    assert len(fake_dummy_worker.api_client.history) == 1
    assert len(fake_dummy_worker.api_client.responses) == 0


def test_list_element_metadata_cached_element(mock_elements_worker_with_cache):
    element = CachedElement.create(id="element_id", type="thing")
    mock_elements_worker_with_cache.api_client = MockApiClient()
    mock_elements_worker_with_cache.api_client.add_response(
        "ListElementMetaData",
        id="element_id",
        response={"id": "metadata_id"},
    )
    assert mock_elements_worker_with_cache.list_element_metadata(element) == {
        "id": "metadata_id"
    }

    assert len(mock_elements_worker_with_cache.api_client.history) == 1
    assert len(mock_elements_worker_with_cache.api_client.responses) == 0
