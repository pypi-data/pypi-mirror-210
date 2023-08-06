from typing import Iterable, List, Optional, Union

from benchling_api_client.v2.beta.api.apps import (
    archive_canvases,
    create_canvas,
    create_session,
    get_benchling_app_manifest,
    get_canvas,
    get_session_by_id,
    list_canvases,
    list_sessions,
    put_benchling_app_manifest,
    unarchive_canvases,
    update_canvas,
    update_session,
)
from benchling_api_client.v2.beta.models.benchling_app_manifest import BenchlingAppManifest
from benchling_api_client.v2.beta.models.canvas import Canvas
from benchling_api_client.v2.beta.models.canvas_create import CanvasCreate
from benchling_api_client.v2.beta.models.canvas_update import CanvasUpdate
from benchling_api_client.v2.beta.models.canvases_archival_change import CanvasesArchivalChange
from benchling_api_client.v2.beta.models.canvases_archive import CanvasesArchive
from benchling_api_client.v2.beta.models.canvases_archive_reason import CanvasesArchiveReason
from benchling_api_client.v2.beta.models.canvases_paginated_list import CanvasesPaginatedList
from benchling_api_client.v2.beta.models.canvases_unarchive import CanvasesUnarchive
from benchling_api_client.v2.beta.models.list_canvases_enabled import ListCanvasesEnabled
from benchling_api_client.v2.beta.models.list_canvases_sort import ListCanvasesSort
from benchling_api_client.v2.beta.models.session import Session
from benchling_api_client.v2.beta.models.session_create import SessionCreate
from benchling_api_client.v2.beta.models.session_update import SessionUpdate
from benchling_api_client.v2.beta.models.sessions_paginated_list import SessionsPaginatedList
from benchling_api_client.v2.stable.types import Response

from benchling_sdk.errors import AppSessionClosedError, raise_for_status
from benchling_sdk.helpers.constants import _translate_to_string_enum
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.serialization_helpers import none_as_unset
from benchling_sdk.services.v2.base_service import BaseService


class V2BetaAppService(BaseService):
    """
    V2-Beta Apps.

    Create and manage Apps on your tenant.

    https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps
    """

    @api_method
    def get_manifest(self, app_id: str) -> BenchlingAppManifest:
        """
        Get app manifest.

        See https://benchling.com/api/v2-beta/reference#/Apps/getBenchlingAppManifest
        """
        response = get_benchling_app_manifest.sync_detailed(client=self.client, app_id=app_id)
        return model_from_detailed(response)

    @api_method
    def update_manifest(self, app_id: str, manifest: BenchlingAppManifest) -> BenchlingAppManifest:
        """
        Update an app manifest.

        See https://benchling.com/api/v2-beta/reference#/Apps/putBenchlingAppManifest
        """
        response = put_benchling_app_manifest.sync_detailed(
            client=self.client, app_id=app_id, yaml_body=manifest
        )
        return model_from_detailed(response)

    @api_method
    def create_canvas(self, canvas: CanvasCreate) -> Canvas:
        """
        Create an App Canvas that a Benchling App can write to and read user interaction from.

        See https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps/createCanvas
        """
        response = create_canvas.sync_detailed(
            client=self.client,
            json_body=canvas,
        )
        return model_from_detailed(response)

    @api_method
    def _canvases_page(
        self,
        app_id: Optional[str] = None,
        feature_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        enabled: Optional[ListCanvasesEnabled] = None,
        archive_reason: Optional[str] = None,
        sort: Optional[Union[str, ListCanvasesSort]] = None,
        next_token: NextToken = None,
        page_size: Optional[int] = None,
    ) -> Response[CanvasesPaginatedList]:
        response = list_canvases.sync_detailed(
            client=self.client,
            app_id=none_as_unset(app_id),
            feature_id=none_as_unset(feature_id),
            resource_id=none_as_unset(resource_id),
            enabled=none_as_unset(enabled),
            archive_reason=none_as_unset(archive_reason),
            sort=none_as_unset(_translate_to_string_enum(ListCanvasesSort, sort)),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )
        raise_for_status(response)
        return response  # type: ignore

    def list_canvases(
        self,
        app_id: Optional[str] = None,
        feature_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        enabled: Optional[ListCanvasesEnabled] = None,
        archive_reason: Optional[str] = None,
        sort: Optional[Union[str, ListCanvasesSort]] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[Session]:
        """
        List canvases.

        See https://benchling.com/api/v2-beta/reference?availability=not-available#/Apps/listCanvases
        """

        def api_call(next_token: NextToken) -> Response[CanvasesPaginatedList]:
            return self._canvases_page(
                app_id=app_id,
                feature_id=feature_id,
                resource_id=resource_id,
                enabled=enabled,
                archive_reason=archive_reason,
                sort=sort,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: CanvasesPaginatedList) -> Optional[List[Canvas]]:
            return body.canvases

        return PageIterator(api_call, results_extractor)

    @api_method
    def get_canvas(self, canvas_id: str) -> Canvas:
        """
        Get the current state of the App Canvas, including user input elements.

        See https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps/getCanvas
        """
        response = get_canvas.sync_detailed(
            client=self.client,
            canvas_id=canvas_id,
        )
        return model_from_detailed(response)

    @api_method
    def update_canvas(self, canvas_id: str, canvas: CanvasUpdate) -> Canvas:
        """
        Update App Canvas.

        See https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps/updateCanvas
        """
        response = update_canvas.sync_detailed(
            client=self.client,
            canvas_id=canvas_id,
            json_body=canvas,
        )
        return model_from_detailed(response)

    @api_method
    def archive_canvases(
        self, canvas_ids: Iterable[str], reason: CanvasesArchiveReason
    ) -> CanvasesArchivalChange:
        """
        Archive App Canvases.

        See https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps/archiveCanvases
        """
        archive_request = CanvasesArchive(reason=reason, canvas_ids=list(canvas_ids))
        response = archive_canvases.sync_detailed(
            client=self.client,
            json_body=archive_request,
        )
        return model_from_detailed(response)

    @api_method
    def unarchive_canvases(self, canvas_ids: Iterable[str]) -> CanvasesArchivalChange:
        """
        Unarchive App Canvases.

        See https://benchling.com/api/v2-beta/reference?stability=not-available#/Apps/unarchiveCanvases
        """
        unarchive_request = CanvasesUnarchive(canvas_ids=list(canvas_ids))
        response = unarchive_canvases.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    # Sessions

    @api_method
    def create_session(self, session: SessionCreate) -> Session:
        """
        Create a new session. Sessions cannot be archived once created.

        See https://benchling.com/api/v2-beta/reference?availability=not-available#/Apps/createSession
        """
        response = create_session.sync_detailed(
            client=self.client,
            json_body=session,
        )
        return model_from_detailed(response)

    @api_method
    def get_session_by_id(self, session_id: str) -> Session:
        """
        Get a session.

        See https://benchling.com/api/v2-beta/reference?availability=not-available#/Apps/getSessionById
        """
        response = get_session_by_id.sync_detailed(
            client=self.client,
            id=session_id,
        )
        return model_from_detailed(response)

    @api_method
    def update_session(self, session_id: str, session: SessionUpdate) -> Session:
        """
        Update session.

        Raises AppSessionClosedError if trying to update a Session that has already been closed.

        See https://benchling.com/api/v2-beta/reference?availability=not-available#/Apps/updateSession
        """
        response = update_session.sync_detailed(
            client=self.client,
            id=session_id,
            json_body=session,
        )
        return model_from_detailed(response, error_types=[AppSessionClosedError])

    @api_method
    def _sessions_page(
        self,
        app_id: Optional[str] = None,
        next_token: NextToken = None,
        page_size: Optional[int] = None,
    ) -> Response[SessionsPaginatedList]:
        response = list_sessions.sync_detailed(
            client=self.client,
            app_id=none_as_unset(app_id),
            next_token=none_as_unset(next_token),
            page_size=none_as_unset(page_size),
        )
        raise_for_status(response)
        return response  # type: ignore

    def list_sessions(
        self, app_id: Optional[str] = None, page_size: Optional[int] = None
    ) -> PageIterator[Session]:
        """
        List all sessions.

        See https://benchling.com/api/v2-beta/reference?availability=not-available#/Apps/listSessions
        """

        def api_call(next_token: NextToken) -> Response[SessionsPaginatedList]:
            return self._sessions_page(
                app_id=app_id,
                next_token=next_token,
                page_size=page_size,
            )

        def results_extractor(body: SessionsPaginatedList) -> Optional[List[Session]]:
            return body.sessions

        return PageIterator(api_call, results_extractor)
