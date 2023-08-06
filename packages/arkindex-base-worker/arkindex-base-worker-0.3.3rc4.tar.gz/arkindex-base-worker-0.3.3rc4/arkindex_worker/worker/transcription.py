# -*- coding: utf-8 -*-
"""
ElementsWorker methods for transcriptions.
"""

from enum import Enum
from typing import Dict, Iterable, List, Optional, Union

from peewee import IntegrityError

from arkindex_worker import logger
from arkindex_worker.cache import CachedElement, CachedTranscription
from arkindex_worker.models import Element


class TextOrientation(Enum):
    """
    Orientation of a transcription's text.
    """

    HorizontalLeftToRight = "horizontal-lr"
    """
    The text is read from top to bottom then left to right.
    This is the default when no orientation is specified.
    """

    HorizontalRightToLeft = "horizontal-rl"
    """
    The text is read from top to bottom then right to left.
    """

    VerticalRightToLeft = "vertical-rl"
    """
    The text is read from right to left then top to bottom.
    """

    VerticalLeftToRight = "vertical-lr"
    """
    The text is read from left to right then top to bottom.
    """


class TranscriptionMixin(object):
    def create_transcription(
        self,
        element: Union[Element, CachedElement],
        text: str,
        confidence: float,
        orientation: TextOrientation = TextOrientation.HorizontalLeftToRight,
    ) -> Optional[Dict[str, Union[str, float]]]:
        """
        Create a transcription on the given element through the API.

        :param element: Element to create a transcription on.
        :param text: Text of the transcription.
        :param confidence: Confidence score, between 0 and 1.
        :param orientation: Orientation of the transcription's text.
        :returns: A dict as returned by the ``CreateTranscription`` API endpoint,
           or None if the worker is in read-only mode.
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        assert text and isinstance(
            text, str
        ), "text shouldn't be null and should be of type str"
        assert orientation and isinstance(
            orientation, TextOrientation
        ), "orientation shouldn't be null and should be of type TextOrientation"
        assert (
            isinstance(confidence, float) and 0 <= confidence <= 1
        ), "confidence shouldn't be null and should be a float in [0..1] range"

        if self.is_read_only:
            logger.warning(
                "Cannot create transcription as this worker is in read-only mode"
            )
            return

        created = self.request(
            "CreateTranscription",
            id=element.id,
            body={
                "text": text,
                "worker_run_id": self.worker_run_id,
                "confidence": confidence,
                "orientation": orientation.value,
            },
        )

        self.report.add_transcription(element.id)

        if self.use_cache:
            # Store transcription in local cache
            try:
                to_insert = [
                    {
                        "id": created["id"],
                        "element_id": element.id,
                        "text": created["text"],
                        "confidence": created["confidence"],
                        "orientation": created["orientation"],
                        "worker_run_id": self.worker_run_id,
                    }
                ]
                CachedTranscription.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcription in local cache: {e}"
                )

        return created

    def create_transcriptions(
        self,
        transcriptions: List[Dict[str, Union[str, float, Optional[TextOrientation]]]],
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Create multiple transcriptions at once on existing elements through the API,
        and creates [CachedTranscription][arkindex_worker.cache.CachedTranscription] instances if cache support is enabled.

        :param transcriptions: A list of dicts representing a transcription each, with the following keys:

            element_id (str)
                Required. UUID of the element to create this transcription on.
            text (str)
                Required. Text of the transcription.
            confidence (float)
                Required. Confidence score between 0 and 1.
            orientation (TextOrientation)
                Optional. Orientation of the transcription's text.

        :returns: A list of dicts as returned in the ``transcriptions`` field by the ``CreateTranscriptions`` API endpoint.
        """

        assert transcriptions and isinstance(
            transcriptions, list
        ), "transcriptions shouldn't be null and should be of type list"

        # Create shallow copies of every transcription to avoid mutating the original payload
        transcriptions_payload = list(map(dict, transcriptions))

        for index, transcription in enumerate(transcriptions_payload):
            element_id = transcription.get("element_id")
            assert element_id and isinstance(
                element_id, str
            ), f"Transcription at index {index} in transcriptions: element_id shouldn't be null and should be of type str"

            text = transcription.get("text")
            assert text and isinstance(
                text, str
            ), f"Transcription at index {index} in transcriptions: text shouldn't be null and should be of type str"

            confidence = transcription.get("confidence")
            assert (
                confidence is not None
                and isinstance(confidence, float)
                and 0 <= confidence <= 1
            ), f"Transcription at index {index} in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"

            orientation = transcription.get(
                "orientation", TextOrientation.HorizontalLeftToRight
            )
            assert orientation and isinstance(
                orientation, TextOrientation
            ), f"Transcription at index {index} in transcriptions: orientation shouldn't be null and should be of type TextOrientation"
            if orientation:
                transcription["orientation"] = orientation.value

        if self.is_read_only:
            logger.warning(
                "Cannot create transcription as this worker is in read-only mode"
            )
            return

        created_trs = self.request(
            "CreateTranscriptions",
            body={
                "worker_run_id": self.worker_run_id,
                "transcriptions": transcriptions_payload,
            },
        )["transcriptions"]

        for created_tr in created_trs:
            self.report.add_transcription(created_tr["element_id"])

        if self.use_cache:
            # Store transcriptions in local cache
            try:
                to_insert = [
                    {
                        "id": created_tr["id"],
                        "element_id": created_tr["element_id"],
                        "text": created_tr["text"],
                        "confidence": created_tr["confidence"],
                        "orientation": created_tr["orientation"],
                        "worker_run_id": self.worker_run_id,
                    }
                    for created_tr in created_trs
                ]
                CachedTranscription.insert_many(to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcriptions in local cache: {e}"
                )

        return created_trs

    def create_element_transcriptions(
        self,
        element: Union[Element, CachedElement],
        sub_element_type: str,
        transcriptions: List[Dict[str, Union[str, float]]],
    ) -> Dict[str, Union[str, bool]]:
        """
        Create multiple elements and transcriptions at once on a single parent element through the API.

        :param element: Element to create elements and transcriptions on.
        :param sub_element_type: Slug of the element type to use for the new elements.
        :param transcriptions: A list of dicts representing an element and transcription each, with the following keys:

            polygon (list(list(int or float)))
                Required. Polygon of the element.
            text (str)
                Required. Text of the transcription.
            confidence (float)
                Required. Confidence score between 0 and 1.
            orientation ([TextOrientation][arkindex_worker.worker.transcription.TextOrientation])
                Optional. Orientation of the transcription's text.
            element_confidence (float)
                Optional. Confidence score of the element between 0 and 1.

        :returns: A list of dicts as returned by the ``CreateElementTranscriptions`` API endpoint.
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        assert sub_element_type and isinstance(
            sub_element_type, str
        ), "sub_element_type shouldn't be null and should be of type str"
        assert transcriptions and isinstance(
            transcriptions, list
        ), "transcriptions shouldn't be null and should be of type list"

        # Create shallow copies of every transcription to avoid mutating the original payload
        transcriptions_payload = list(map(dict, transcriptions))

        for index, transcription in enumerate(transcriptions_payload):
            text = transcription.get("text")
            assert text and isinstance(
                text, str
            ), f"Transcription at index {index} in transcriptions: text shouldn't be null and should be of type str"

            confidence = transcription.get("confidence")
            assert (
                confidence is not None
                and isinstance(confidence, float)
                and 0 <= confidence <= 1
            ), f"Transcription at index {index} in transcriptions: confidence shouldn't be null and should be a float in [0..1] range"

            orientation = transcription.get(
                "orientation", TextOrientation.HorizontalLeftToRight
            )
            assert orientation and isinstance(
                orientation, TextOrientation
            ), f"Transcription at index {index} in transcriptions: orientation shouldn't be null and should be of type TextOrientation"
            if orientation:
                transcription["orientation"] = orientation.value

            polygon = transcription.get("polygon")
            assert polygon and isinstance(
                polygon, list
            ), f"Transcription at index {index} in transcriptions: polygon shouldn't be null and should be of type list"
            assert (
                len(polygon) >= 3
            ), f"Transcription at index {index} in transcriptions: polygon should have at least three points"
            assert all(
                isinstance(point, list) and len(point) == 2 for point in polygon
            ), f"Transcription at index {index} in transcriptions: polygon points should be lists of two items"
            assert all(
                isinstance(coord, (int, float)) for point in polygon for coord in point
            ), f"Transcription at index {index} in transcriptions: polygon points should be lists of two numbers"

            element_confidence = transcription.get("element_confidence")
            assert element_confidence is None or (
                isinstance(element_confidence, float) and 0 <= element_confidence <= 1
            ), f"Transcription at index {index} in transcriptions: element_confidence should be either null or a float in [0..1] range"

        if self.is_read_only:
            logger.warning(
                "Cannot create transcriptions as this worker is in read-only mode"
            )
            return

        annotations = self.request(
            "CreateElementTranscriptions",
            id=element.id,
            body={
                "element_type": sub_element_type,
                "worker_run_id": self.worker_run_id,
                "transcriptions": transcriptions_payload,
                "return_elements": True,
            },
        )

        for annotation in annotations:
            if annotation["created"]:
                logger.debug(
                    f"A sub_element of {element.id} with type {sub_element_type} was created during transcriptions bulk creation"
                )
                self.report.add_element(element.id, sub_element_type)
            self.report.add_transcription(annotation["element_id"])

        if self.use_cache:
            # Store transcriptions and their associated element (if created) in local cache
            created_ids = set()
            elements_to_insert = []
            transcriptions_to_insert = []
            for index, annotation in enumerate(annotations):
                transcription = transcriptions[index]

                if annotation["element_id"] not in created_ids:
                    # Even if the API says the element already existed in the DB,
                    # we need to check if it is available in the local cache.
                    # Peewee does not have support for SQLite's INSERT OR IGNORE,
                    # so we do the check here, element by element.
                    try:
                        CachedElement.get_by_id(annotation["element_id"])
                    except CachedElement.DoesNotExist:
                        elements_to_insert.append(
                            {
                                "id": annotation["element_id"],
                                "parent_id": element.id,
                                "type": sub_element_type,
                                "image_id": element.image_id,
                                "polygon": transcription["polygon"],
                                "worker_run_id": self.worker_run_id,
                                "confidence": transcription.get("element_confidence"),
                            }
                        )

                    created_ids.add(annotation["element_id"])

                transcriptions_to_insert.append(
                    {
                        "id": annotation["id"],
                        "element_id": annotation["element_id"],
                        "text": transcription["text"],
                        "confidence": transcription["confidence"],
                        "orientation": transcription.get(
                            "orientation", TextOrientation.HorizontalLeftToRight
                        ).value,
                        "worker_run_id": self.worker_run_id,
                    }
                )

            try:
                CachedElement.insert_many(elements_to_insert).execute()
                CachedTranscription.insert_many(transcriptions_to_insert).execute()
            except IntegrityError as e:
                logger.warning(
                    f"Couldn't save created transcriptions in local cache: {e}"
                )

        return annotations

    def list_transcriptions(
        self,
        element: Union[Element, CachedElement],
        element_type: Optional[str] = None,
        recursive: Optional[bool] = None,
        worker_version: Optional[Union[str, bool]] = None,
    ) -> Union[Iterable[dict], Iterable[CachedTranscription]]:
        """
        List transcriptions on an element.

        :param element: The element to list transcriptions on.
        :param element_type: Restrict to transcriptions whose elements have an element type with this slug.
        :param recursive: Include transcriptions of any descendant of this element, recursively.
        :param worker_version: Restrict to transcriptions created by a worker version with this UUID. Set to False to look for manually created transcriptions.
        :returns: An iterable of dicts representing each transcription,
           or an iterable of CachedTranscription when cache support is enabled.
        """
        assert element and isinstance(
            element, (Element, CachedElement)
        ), "element shouldn't be null and should be an Element or CachedElement"
        query_params = {}
        if element_type:
            assert isinstance(element_type, str), "element_type should be of type str"
            query_params["element_type"] = element_type
        if recursive is not None:
            assert isinstance(recursive, bool), "recursive should be of type bool"
            query_params["recursive"] = recursive
        if worker_version is not None:
            assert isinstance(
                worker_version, (str, bool)
            ), "worker_version should be of type str or bool"
            if isinstance(worker_version, bool):
                assert (
                    worker_version is False
                ), "if of type bool, worker_version can only be set to False"
            query_params["worker_version"] = worker_version

        if self.use_cache:
            if not recursive:
                # In this case we don't have to return anything, it's easier to use an
                # impossible condition (False) rather than filtering by type for nothing
                if element_type and element_type != element.type:
                    return CachedTranscription.select().where(False)
                transcriptions = CachedTranscription.select().where(
                    CachedTranscription.element_id == element.id
                )
            else:
                base_case = (
                    CachedElement.select()
                    .where(CachedElement.id == element.id)
                    .cte("base", recursive=True)
                )
                recursive = CachedElement.select().join(
                    base_case, on=(CachedElement.parent_id == base_case.c.id)
                )
                cte = base_case.union_all(recursive)
                transcriptions = (
                    CachedTranscription.select()
                    .join(cte, on=(CachedTranscription.element_id == cte.c.id))
                    .with_cte(cte)
                )

                if element_type:
                    transcriptions = transcriptions.where(cte.c.type == element_type)

            if worker_version is not None:
                # If worker_version=False, filter by manual worker_version e.g. None
                worker_version_id = worker_version if worker_version else None
                transcriptions = transcriptions.where(
                    CachedTranscription.worker_version_id == worker_version_id
                )
        else:
            transcriptions = self.api_client.paginate(
                "ListTranscriptions", id=element.id, **query_params
            )

        return transcriptions
