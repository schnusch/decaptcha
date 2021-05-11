import asyncio
import logging
import sys
from aiohttp import web # type: ignore
from .  import add_routes, wrap_decaptcha_solve
from .. import DeCaptcha, ReCaptchaHTMLGenerator

async def amain():
    htmlgen = ReCaptchaHTMLGenerator()
    decaptcha = DeCaptcha(htmlgen)

    app = web.Application()
    add_routes(app, solve=wrap_decaptcha_solve(decaptcha.solve))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 8100)

    await site.start()
    await decaptcha.run()

print(r'''
curl -d '{"task":{"type":"HCaptchaTaskProxyless","websiteURL":"https://decaptcha.test/","websiteKey":"6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"}}' http://127.0.0.1:8100/createTask && echo && \
curl -d '{"task":{"type":"HCaptchaTaskProxyless","websiteURL":"https://decaptcha.test/","websiteKey":"6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"}}' http://127.0.0.1:8100/createTask && echo && \
printf 'Enter first task id: ' && read taskid1 && \
printf 'Enter second task id: ' && read taskid2 && \
curl -d '{"taskId":"'"$taskid2"'"}' http://127.0.0.1:8100/getTaskResult && echo && \
curl -d '{"taskId":"'"$taskid1"'"}' http://127.0.0.1:8100/getTaskResult && echo
''')

logging.basicConfig(format='[%(asctime)s] %(levelname)-8s %(name)-48s %(message)s',
                    level=logging.DEBUG, stream=sys.stderr)
asyncio.run(amain())
