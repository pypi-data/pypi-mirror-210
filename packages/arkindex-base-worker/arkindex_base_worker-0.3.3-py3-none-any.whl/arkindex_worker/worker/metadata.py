# -*- coding: utf-8 -*-
"""
ElementsWorker methods for metadata.
"""

from enum import Enum
from typing import Dict, List, Optional, Union

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement
from arkindex_worker.models import Element


class MetaType(Enum):
    """
    Type of a metadata.
    """

    Text = "text"
    """
    A regular string with no special interpretation.
    """

    HTML = "html"
    """
    A metadata with a string value that should be interpreted as HTML content.
    The allowed HTML tags are restricted for security reasons.
    """

    Date = "date"
    """
    A metadata with a string value that should be interpreted as a date.
    The date should be formatted as an ISO 8601 date (``YYYY-MM-DD``).
    """

    Location = "location"
    """
    A metadata with a string value that should be interpreted as a location.
    """

    Reference = "reference"
    """
    A metadata with a string value that should be interpreted as an external identifier
    to this element, for example to preserve a link to the original data before it was
    imported into Arkindex.
    """

    Numeric = "numeric"
    """
    A metadata with a floating point value.
    """

    URL = "url"
    """
    A metadata with a string value that should be interpreted as an URL.
    Only the ``http`` and ``https`` schemes are allowed.
    """


class MetaDataMixin(object):
    def create_metadata(
        self,
        element: Union[Element, CachedElement],
        type: MetaType,
        name: str,
        value: str,
        entity: Optional[str] = None,
    ) -> str:
        """
        Create a metadata on the given element through API.

        :param element: The element to create a metadata on.
        :param type: Type of the metadata.
        :param name: Name of the metadata.
        :param value: Value of the metadata.
        :param entity: UUID of an entity this metadata is related to.
        :returns: UUID of the created metadata.
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be of type Element or CachedElement"
        assert type and isinstance(
            type, MetaType
        ), "type shouldn't be null and should be of type MetaType"
        assert name and isinstance(
            name, str
        ), "name shouldn't be null and should be of type str"
        assert value and isinstance(
            value, str
        ), "value shouldn't be null and should be of type str"
        if entity:
            assert isinstance(entity, str), "entity should be of type str"
        if self.is_read_only:
            logger.warning("Cannot create metadata as this worker is in read-only mode")
            return

        metadata = self.request(
            "CreateMetaData",
            id=element.id,
            body={
                "type": type.value,
                "name": name,
                "value": value,
                "entity_id": entity,
                "worker_run_id": self.worker_run_id,
            },
        )
        self.report.add_metadata(element.id, metadata["id"], type.value, name)

        return metadata["id"]

    def create_metadatas(
        self,
        element: Union[Element, CachedElement],
        metadatas: List[
            Dict[
                str, Union[MetaType, str, Union[str, Union[int, float]], Optional[str]]
            ]
        ],
    ) -> List[Dict[str, str]]:
        """
        Create multiple metadatas on an existing element.
        This method does not support cache.

        :param element Element: The element to create multiple metadata on.
        :param metadata_list List(Dict): The list of dict whose keys are the following:
            - type : MetaType
            - name : str
            - value : Union[str, Union[int, float]]
            - entity_id : Union[str, None]
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be of type Element or CachedElement"

        assert metadatas and isinstance(
            metadatas, list
        ), "type shouldn't be null and should be of type list of Dict"

        # Make a copy to avoid modifying the metadata_list argument
        metas = []
        for index, metadata in enumerate(metadatas):
            assert isinstance(
                metadata, dict
            ), f"Element at index {index} in metadata_list: Should be of type dict"

            assert metadata.get("type") and isinstance(
                metadata.get("type"), MetaType
            ), "type shouldn't be null and should be of type MetaType"

            assert metadata.get("name") and isinstance(
                metadata.get("name"), str
            ), "name shouldn't be null and should be of type str"

            assert metadata.get("value") is not None and isinstance(
                metadata.get("value"), (str, float, int)
            ), "value shouldn't be null and should be of type (str or float or int)"

            assert metadata.get("entity_id") is None or isinstance(
                metadata.get("entity_id"), str
            ), "entity_id should be None or a str"

            metas.append(
                {
                    "type": metadata.get("type").value,
                    "name": metadata.get("name"),
                    "value": metadata.get("value"),
                    "entity_id": metadata.get("entity_id"),
                }
            )

        if self.is_read_only:
            logger.warning("Cannot create metadata as this worker is in read-only mode")
            return

        created_metadatas = self.request(
            "CreateMetaDataBulk",
            id=element.id,
            body={
                "worker_run_id": self.worker_run_id,
                "metadata_list": metas,
            },
        )["metadata_list"]

        for meta in created_metadatas:
            self.report.add_metadata(element.id, meta["id"], meta["type"], meta["name"])

        return created_metadatas

    def list_element_metadata(
        self, element: Union[Element, CachedElement]
    ) -> List[Dict[str, str]]:
        """
        List all metadata linked to an element.
        This method does not support cache.

        :param element: The element to list metadata on.
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be of type Element or CachedElement"

        return self.api_client.paginate("ListElementMetaData", id=element.id)
