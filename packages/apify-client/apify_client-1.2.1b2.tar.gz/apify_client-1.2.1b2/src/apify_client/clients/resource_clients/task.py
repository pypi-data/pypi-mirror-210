from typing import Any, Dict, List, Optional, cast

from ..._errors import ApifyApiError
from ..._utils import (
    _catch_not_found_or_throw,
    _encode_webhook_list_to_base64,
    _filter_out_none_values_recursively,
    _maybe_extract_enum_member_value,
    _parse_date_fields,
    _pluck_data,
    ignore_docs,
)
from ...consts import ActorJobStatus, MetaOrigin
from ..base import ResourceClient, ResourceClientAsync
from .run import RunClient, RunClientAsync
from .run_collection import RunCollectionClient, RunCollectionClientAsync
from .webhook_collection import WebhookCollectionClient, WebhookCollectionClientAsync


def _get_task_representation(
    actor_id: Optional[str] = None,
    name: Optional[str] = None,
    task_input: Optional[Dict] = None,
    build: Optional[str] = None,
    memory_mbytes: Optional[int] = None,
    timeout_secs: Optional[int] = None,
    title: Optional[str] = None,
) -> Dict:
    return {
        'actId': actor_id,
        'name': name,
        'options': {
            'build': build,
            'memoryMbytes': memory_mbytes,
            'timeoutSecs': timeout_secs,
        },
        'input': task_input,
        'title': title,
    }


class TaskClient(ResourceClient):
    """Sub-client for manipulating a single task."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskClient."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    def get(self) -> Optional[Dict]:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            dict, optional: The retrieved task
        """
        return self._get()

    def update(
        self,
        *,
        name: Optional[str] = None,
        task_input: Optional[Dict] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Update the task with specified fields.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task

        Args:
            name (str, optional): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input dictionary
            title (str, optional): A human-friendly equivalent of the name

        Returns:
            dict: The updated task
        """
        task_representation = _get_task_representation(
            name=name,
            task_input=task_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            title=title,
        )

        return self._update(_filter_out_none_values_recursively(task_representation))

    def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        return self._delete()

    def start(
        self,
        *,
        task_input: Optional[Dict[str, Any]] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        wait_for_finish: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Start the task and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Task input dictionary
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 300.
            webhooks (list of dict, optional): Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks)
                                               associated with the actor run which can be used to receive a notification,
                                               e.g. when the actor finished or failed.
                                               If you already have a webhook set up for the actor or task, you do not have to add it again here.
                                               Each webhook is represented by a dictionary containing these items:
                                               * ``event_types``: list of ``WebhookEventType`` values which trigger the webhook
                                               * ``request_url``: URL to which to send the webhook HTTP request
                                               * ``payload_template`` (optional): Optional template for the request payload

        Returns:
            dict: The run object
        """
        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=_encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    def call(
        self,
        *,
        task_input: Optional[Dict[str, Any]] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
        wait_secs: Optional[int] = None,
    ) -> Optional[Dict]:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Task input dictionary
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            webhooks (list, optional): Specifies optional webhooks associated with the actor run, which can be used to receive a notification
                                       e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
                                       you do not have to add it again here.
            wait_secs (int, optional): The maximum number of seconds the server waits for the task run to finish. If not provided, waits indefinitely.

        Returns:
            dict: The run object
        """
        started_run = self.start(
            task_input=task_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    def get_input(self) -> Optional[Dict]:
        """Retrieve the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input

        Returns:
            dict, optional: Retrieved task input
        """
        try:
            response = self.http_client.call(
                url=self._url('input'),
                method='GET',
                params=self._params(),
            )
            return cast(Dict, response.json())
        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)
        return None

    def update_input(self, *, task_input: Dict) -> Dict:
        """Update the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input

        Returns:
            dict, Retrieved task input
        """
        response = self.http_client.call(
            url=self._url('input'),
            method='PUT',
            params=self._params(),
            json=task_input,
        )
        return cast(Dict, response.json())

    def runs(self) -> RunCollectionClient:
        """Retrieve a client for the runs of this task."""
        return RunCollectionClient(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(self, *, status: Optional[ActorJobStatus] = None, origin: Optional[MetaOrigin] = None) -> RunClient:
        """Retrieve the client for the last run of this task.

        Last run is retrieved based on the start time of the runs.

        Args:
            status (ActorJobStatus, optional): Consider only runs with this status.
            origin (MetaOrigin, optional): Consider only runs started with this origin.

        Returns:
            RunClient: The resource client for the last run of this task.
        """
        return RunClient(**self._sub_resource_init_options(
            resource_id='last',
            resource_path='runs',
            params=self._params(
                status=_maybe_extract_enum_member_value(status),
                origin=_maybe_extract_enum_member_value(origin),
            ),
        ))

    def webhooks(self) -> WebhookCollectionClient:
        """Retrieve a client for webhooks associated with this task."""
        return WebhookCollectionClient(**self._sub_resource_init_options())


class TaskClientAsync(ResourceClientAsync):
    """Async sub-client for manipulating a single task."""

    @ignore_docs
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the TaskClientAsync."""
        resource_path = kwargs.pop('resource_path', 'actor-tasks')
        super().__init__(*args, resource_path=resource_path, **kwargs)

    async def get(self) -> Optional[Dict]:
        """Retrieve the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/get-task

        Returns:
            dict, optional: The retrieved task
        """
        return await self._get()

    async def update(
        self,
        *,
        name: Optional[str] = None,
        task_input: Optional[Dict] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        title: Optional[str] = None,
    ) -> Dict:
        """Update the task with specified fields.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/update-task

        Args:
            name (str, optional): Name of the task
            build (str, optional): Actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            task_input (dict, optional): Task input dictionary
            title (str, optional): A human-friendly equivalent of the name

        Returns:
            dict: The updated task
        """
        task_representation = _get_task_representation(
            name=name,
            task_input=task_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            title=title,
        )

        return await self._update(_filter_out_none_values_recursively(task_representation))

    async def delete(self) -> None:
        """Delete the task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-object/delete-task
        """
        return await self._delete()

    async def start(
        self,
        *,
        task_input: Optional[Dict[str, Any]] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        wait_for_finish: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
    ) -> Dict:
        """Start the task and immediately return the Run object.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Task input dictionary
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            wait_for_finish (int, optional): The maximum number of seconds the server waits for the run to finish.
                                               By default, it is 0, the maximum value is 300.
            webhooks (list of dict, optional): Optional ad-hoc webhooks (https://docs.apify.com/webhooks/ad-hoc-webhooks)
                                               associated with the actor run which can be used to receive a notification,
                                               e.g. when the actor finished or failed.
                                               If you already have a webhook set up for the actor or task, you do not have to add it again here.
                                               Each webhook is represented by a dictionary containing these items:
                                               * ``event_types``: list of ``WebhookEventType`` values which trigger the webhook
                                               * ``request_url``: URL to which to send the webhook HTTP request
                                               * ``payload_template`` (optional): Optional template for the request payload

        Returns:
            dict: The run object
        """
        request_params = self._params(
            build=build,
            memory=memory_mbytes,
            timeout=timeout_secs,
            waitForFinish=wait_for_finish,
            webhooks=_encode_webhook_list_to_base64(webhooks) if webhooks is not None else None,
        )

        response = await self.http_client.call(
            url=self._url('runs'),
            method='POST',
            headers={'content-type': 'application/json; charset=utf-8'},
            json=task_input,
            params=request_params,
        )

        return _parse_date_fields(_pluck_data(response.json()))

    async def call(
        self,
        *,
        task_input: Optional[Dict[str, Any]] = None,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
        webhooks: Optional[List[Dict]] = None,
        wait_secs: Optional[int] = None,
    ) -> Optional[Dict]:
        """Start a task and wait for it to finish before returning the Run object.

        It waits indefinitely, unless the wait_secs argument is provided.

        https://docs.apify.com/api/v2#/reference/actor-tasks/run-collection/run-task

        Args:
            task_input (dict, optional): Task input dictionary
            build (str, optional): Specifies the actor build to run. It can be either a build tag or build number.
                                   By default, the run uses the build specified in the task settings (typically latest).
            memory_mbytes (int, optional): Memory limit for the run, in megabytes.
                                           By default, the run uses a memory limit specified in the task settings.
            timeout_secs (int, optional): Optional timeout for the run, in seconds. By default, the run uses timeout specified in the task settings.
            webhooks (list, optional): Specifies optional webhooks associated with the actor run, which can be used to receive a notification
                                       e.g. when the actor finished or failed. Note: if you already have a webhook set up for the actor or task,
                                       you do not have to add it again here.
            wait_secs (int, optional): The maximum number of seconds the server waits for the task run to finish. If not provided, waits indefinitely.

        Returns:
            dict: The run object
        """
        started_run = await self.start(
            task_input=task_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
            webhooks=webhooks,
        )

        return await self.root_client.run(started_run['id']).wait_for_finish(wait_secs=wait_secs)

    async def get_input(self) -> Optional[Dict]:
        """Retrieve the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/get-task-input

        Returns:
            dict, optional: Retrieved task input
        """
        try:
            response = await self.http_client.call(
                url=self._url('input'),
                method='GET',
                params=self._params(),
            )
            return cast(Dict, response.json())
        except ApifyApiError as exc:
            _catch_not_found_or_throw(exc)
        return None

    async def update_input(self, *, task_input: Dict) -> Dict:
        """Update the default input for this task.

        https://docs.apify.com/api/v2#/reference/actor-tasks/task-input-object/update-task-input

        Returns:
            dict, Retrieved task input
        """
        response = await self.http_client.call(
            url=self._url('input'),
            method='PUT',
            params=self._params(),
            json=task_input,
        )
        return cast(Dict, response.json())

    def runs(self) -> RunCollectionClientAsync:
        """Retrieve a client for the runs of this task."""
        return RunCollectionClientAsync(**self._sub_resource_init_options(resource_path='runs'))

    def last_run(self, *, status: Optional[ActorJobStatus] = None, origin: Optional[MetaOrigin] = None) -> RunClientAsync:
        """Retrieve the client for the last run of this task.

        Last run is retrieved based on the start time of the runs.

        Args:
            status (ActorJobStatus, optional): Consider only runs with this status.
            origin (MetaOrigin, optional): Consider only runs started with this origin.

        Returns:
            RunClientAsync: The resource client for the last run of this task.
        """
        return RunClientAsync(**self._sub_resource_init_options(
            resource_id='last',
            resource_path='runs',
            params=self._params(
                status=_maybe_extract_enum_member_value(status),
                origin=_maybe_extract_enum_member_value(origin),
            ),
        ))

    def webhooks(self) -> WebhookCollectionClientAsync:
        """Retrieve a client for webhooks associated with this task."""
        return WebhookCollectionClientAsync(**self._sub_resource_init_options())
