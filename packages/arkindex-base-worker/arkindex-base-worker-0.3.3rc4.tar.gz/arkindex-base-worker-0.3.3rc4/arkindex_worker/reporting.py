# -*- coding: utf-8 -*-
"""
Generator for the ``ml_report.json`` file, to report created worker results and exceptions.
"""

import json
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from uuid import UUID

from apistar.exceptions import ErrorResponse

from arkindex_worker import logger
from arkindex_worker.models import Transcription


class Reporter(object):
    """
    Helper to generate an ``ml_report.json`` artifact.
    """

    def __init__(
        self,
        name: Optional[str] = "Unknown worker",
        slug: Optional[str] = "unknown-slug",
        version: Optional[str] = None,
        **kwargs,
    ):
        self.report_data = {
            "name": name,
            "slug": slug,
            "version": version,
            "started": datetime.utcnow().isoformat(),
            "elements": {},
        }
        logger.info(f"Starting ML report for {name}")

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.report_data["slug"])

    def _get_element(self, element_id):
        return self.report_data["elements"].setdefault(
            str(element_id),
            {
                "started": datetime.utcnow().isoformat(),
                # Created element counts, by type slug
                "elements": {},
                # Created transcriptions count
                "transcriptions": 0,
                # Created classification counts, by class
                "classifications": {},
                # Created entities ({"id": "", "type": "", "name": ""}) from this element
                "entities": [],
                # Created transcription entities ({"transcription_id": "", "entity_id": ""}) from this element
                "transcription_entities": [],
                # Created metadata ({"id": "", "type": "", "name": ""}) from this element
                "metadata": [],
                "errors": [],
            },
        )

    def process(self, element_id: Union[str, UUID]):
        """
        Report that a specific element ID is being processed.

        :param element_id: ID of the element being processed.
        """
        # Just call the element initializer
        self._get_element(element_id)

    def add_element(self, parent_id: Union[str, UUID], type: str, type_count: int = 1):
        """
        Report creating an element as a child of another.

        :param parent_id: ID of the parent element.
        :param type: Slug of the type of the child element.
        :param type_count: How many elements of this type were created.
        """
        elements = self._get_element(parent_id)["elements"]
        elements.setdefault(type, 0)
        elements[type] += type_count

    def add_classification(self, element_id: Union[str, UUID], class_name: str):
        """
        Report creating a classification on an element.

        :param element_id: ID of the element.
        :param class_name: Name of the ML class of the new classification.
        """
        classifications = self._get_element(element_id)["classifications"]
        classifications.setdefault(class_name, 0)
        classifications[class_name] += 1

    def add_classifications(
        self, element_id: Union[str, UUID], classifications: List[Dict[str, str]]
    ):
        """
        Report creating one or more classifications at once on an element.

        :param element_id: ID of the element.
        :param classifications: List of classifications.
           Each classification is represented as a ``dict`` with a ``class_name`` key
           holding the name of the ML class being used.
        """
        assert isinstance(
            classifications, list
        ), "A list is required for classifications"
        element = self._get_element(element_id)
        # Retrieve the previous existing classification counts, if any
        counter = Counter(**element["classifications"])
        # Add the new ones
        counter.update(
            [classification["class_name"] for classification in classifications]
        )
        element["classifications"] = dict(counter)

    def add_transcription(self, element_id: Union[str, UUID], count=1):
        """
        Report creating a transcription on an element.

        :param element_id: ID of the element.
        :param count: Number of transcriptions created at once
        """
        self._get_element(element_id)["transcriptions"] += count

    def add_entity(
        self,
        element_id: Union[str, UUID],
        entity_id: Union[str, UUID],
        type: str,
        name: str,
    ):
        """
        Report creating an entity on an element.

        :param element_id: ID of the element.
        :param entity_id: ID of the new entity.
        :param type: Type of the entity.
        :param name: Name of the entity.
        """
        entities = self._get_element(element_id)["entities"]
        entities.append({"id": entity_id, "type": type, "name": name})

    def add_transcription_entity(
        self,
        entity_id: Union[str, UUID],
        transcription: Transcription,
        transcription_entity_id: Union[str, UUID],
    ):
        """
        Report creating a transcription entity on an element.

        :param entity_id: ID of the entity element.
        :param transcription: Transcription to add the entity on
        :param transcription_entity_id: ID of the transcription entity that is created.
        """
        transcription_entities = self._get_element(transcription.element.id)[
            "transcription_entities"
        ]
        transcription_entities.append(
            {
                "transcription_id": transcription.id,
                "entity_id": entity_id,
                "transcription_entity_id": transcription_entity_id,
            }
        )

    def add_entity_link(self, *args, **kwargs):
        """
        Report creating an entity link. Not currently supported.

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def add_entity_role(self, *args, **kwargs):
        """
        Report creating an entity role. Not currently supported.

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def add_metadata(
        self,
        element_id: Union[str, UUID],
        metadata_id: Union[str, UUID],
        type: str,
        name: str,
    ):
        """
        Report creating a metadata from an element.

        :param element_id: ID of the element.
        :param metadata_id: ID of the new metadata.
        :param type: Type of the metadata.
        :param name: Name of the metadata.
        """
        metadata = self._get_element(element_id)["metadata"]
        metadata.append({"id": metadata_id, "type": type, "name": name})

    def error(self, element_id: Union[str, UUID], exception: Exception):
        """
        Report that a Python exception occurred when processing an element.

        :param element_id: ID of the element.
        :param exception: A Python exception.
        """
        error_data = {
            "class": exception.__class__.__name__,
            "message": str(exception),
        }
        if exception.__traceback__ is not None:
            error_data["traceback"] = "\n".join(
                traceback.format_tb(exception.__traceback__)
            )

        if isinstance(exception, ErrorResponse):
            error_data["message"] = exception.title
            error_data["status_code"] = exception.status_code
            error_data["content"] = exception.content

        self._get_element(element_id)["errors"].append(error_data)

    def save(self, path: Union[str, Path]):
        """
        Save the ML report to the specified path.

        :param path: Path to save the ML report to.
        """
        logger.info(f"Saving ML report to {path}")
        with open(path, "w") as f:
            json.dump(self.report_data, f)
