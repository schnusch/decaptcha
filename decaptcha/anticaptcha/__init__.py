import asyncio
import functools
import json
import jsonschema # type: ignore
import logging
import uuid
from aiohttp import web # type: ignore
from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    Optional,
    Tuple,
)
from . import schemas
from .errors import *
from .. import CaptchaRequest, CaptchaSuccess

keep_alive = 25

Task = 'Task'
TaskID = str
Solution = 'Solution'
CaptchaSolveFunc = Callable[[Task], Awaitable[Solution]]

class TaskQueue:
    def __init__(self, solve: CaptchaSolveFunc):
        self.tasks = {}    # type: Mapping[TaskID, asyncio.Task]
        self.solve = solve # type: CaptchaSolveFunc

    def create_task_id(self) -> TaskID:
        while True:
            task_id = str(uuid.uuid4())
            if task_id not in self.tasks:
                return task_id

    def create_task(self,
                    task_id:      TaskID,
                    task:         Task,
                    callback_url: Optional[str] = None) -> asyncio.Task:
        captcha_task = asyncio.create_task(self.solve(task))

        @captcha_task.add_done_callback
        def _(_: asyncio.Task) -> None:
            logger = logging.getLogger('CaptchaTask#%s' % task_id)
            logger.info('done')
            # TODO call callbackUrl
            if callback_url is not None:
                logger.error('callbackUrl not supported')

        return captcha_task

    async def enqueue_task(self,
                           task:         Task,
                           callback_url: Optional[str] = None) -> TaskID:
        task_id = self.create_task_id()
        captcha_task = self.create_task(task_id, task, callback_url)
        self.tasks[task_id] = captcha_task
        return task_id

    def __getitem__(self, task_id: TaskID) -> asyncio.Task:
        return self.tasks[task_id]

    def __delitem__(self, task_id: TaskID) -> None:
        del self.tasks[task_id]

def short_json(data):
    return json.dumps(data, separators=(',', ':'))

def JsonResponse(data) -> web.Response:
    return web.Response(text=short_json(data), content_type='application/json',
                        charset='utf-8')

async def create_task(task_queue: TaskQueue,
                      request:    web.Request) -> web.Response:
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        raise web.HTTPBadRequest(text='invalid JSON')
    try:
        jsonschema.validate(data, schemas.createTask)
    except jsonschema.ValidationError as e:
        raise web.HTTPBadRequest(text='malformed request: ' + e.message)

    task = data['task']
    task_id = await task_queue.enqueue_task(task, data.get('callbackUrl'))
    return JsonResponse({
        'errorId': 0,
        'taskId': task_id,
    })

async def get_task_result(task_queue: TaskQueue,
                          request:    web.Request):
    try:
        data = await request.json()
    except json.decoder.JSONDecodeError:
        raise web.HTTPBadRequest(text='invalid JSON')
    try:
        jsonschema.validate(data, schemas.getTaskResult)
    except jsonschema.ValidationError as e:
        raise web.HTTPBadRequest(text='malformed request: ' + e.message)

    task_id = data['taskId']
    try:
        captcha_task = task_queue[task_id]
    except KeyError:
        return JsonResponse(ERROR_NO_SUCH_CAPCHA_ID)

    response = web.StreamResponse()
    response.content_type = 'application/json'
    response.enable_chunked_encoding()
    await response.prepare(request)

    logger = logging.getLogger('CaptchaTask#%s' % task_id)
    logger.info('awaiting...')
    # wait for the task to be done
    while True:
        await asyncio.wait([
            asyncio.sleep(keep_alive),
            captcha_task,
        ], return_when=asyncio.FIRST_COMPLETED)
        if captcha_task.done():
            result = captcha_task.result()
            break
        # send keep-alive byte
        await response.write(b' ')

    await response.write(short_json({
        'errorId': 0,
        'status': 'ready',
        'solution': result,
    }).encode('utf-8'))
    await response.write_eof()
    del task_queue[task_id]

def add_routes(app:   web.Application,
               solve: CaptchaSolveFunc) -> None:
    task_queue = TaskQueue(solve)
    app.router.add_route('POST', '/createTask',
                         functools.partial(create_task, task_queue))
    app.router.add_route('POST', '/getTaskResult',
                         functools.partial(get_task_result, task_queue))

def wrap_decaptcha_solve(solve: Callable[[CaptchaRequest], Awaitable[CaptchaSuccess]]) -> Callable[[Task], Awaitable[Solution]]:
    async def wrapped(task: Task) -> Solution:
        request = {
            'url': task['websiteURL'],
            'options': {
                'websiteKey': task['websiteKey'],
                'invisible':  task.get('isInvisible', False),
            }
        } # type: CaptchaRequest
        response = await solve(request)
        return response['response']
    return wrapped
