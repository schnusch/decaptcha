"""
decaptcha
Copyright (C) 2021  schnusch

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import json
import logging
import os
from typing import (
	Any,
	Awaitable,
	Callable,
	cast,
	Final,
	List,
	Literal,
	Mapping,
	NamedTuple,
	Optional,
	TypedDict,
	Union,
)

import gi # type: ignore
gi.require_version('GLib',    '2.0')
gi.require_version('Gtk',     '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import GLib    as glib   # type: ignore
from gi.repository import Gtk     as gtk    # type: ignore
from gi.repository import WebKit2 as webkit # type: ignore

import jsonschema # type: ignore

try:
	from youtube_dl.utils import random_user_agent # type: ignore
except ImportError:
	def random_user_agent() -> None:
		return None


class CaptchaRequest(TypedDict):
	url:     str
	options: Mapping[str, Any]
def parse_captcha_request(data: str) -> CaptchaRequest:
	req = json.loads(data)
	jsonschema.validate(req, {
		'type': 'object',
		'required': ['url'],
		'properties': {
			'url':     {'type': 'string'},
			'options': {'type': 'object'},
		},
		'additionalProperties': True,
	})
	req.setdefault('options', {})
	return req

class CaptchaSuccess(TypedDict):
#	error:    Optional[Literal[False]] # Optional[T] is only an alias for Union[T, None], so not applicable here
	response: Mapping[str, Any]
class CaptchaError(TypedDict):
	error:  Literal[True]
	reason: str
CaptchaResponse = Union[CaptchaSuccess, CaptchaError]

class CaptchaException(Exception):
	def to_dict(self) -> CaptchaError:
		return {'error': True, 'reason': str(self)}

class RequestTuple(NamedTuple):
	request:       CaptchaRequest
	set_result:    Callable[[CaptchaSuccess],   None]
	set_exception: Callable[[CaptchaException], None]


def read_resource(name: str) -> str:
	with open(os.path.join(os.path.dirname(__file__), name), 'r', encoding='utf-8') as fp:
		return fp.read()

class HTMLGenerator:
	def __init__(self):
		pass

	@staticmethod
	def escape_xml(x: str) -> str:
		for a, b in [('&', '&amp;'), ('<', '&lt;'), ('"', '&dquot;'), ("'", '&sqout;')]:
			x = x.replace(a, b)
		return x

	@staticmethod
	def xml_attrs(attrs: Mapping[str, str]) -> str:
		return ' '.join('%s="%s"' % (k, HTMLGenerator.escape_xml(v)) for k, v in attrs.items())

	def generate(self, req: CaptchaRequest) -> str:
		raise NotImplementedError

class ReCaptchaHTMLGenerator(HTMLGenerator):
	#  testing site key, see https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do
	fallback_sitekey = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'

	def __init__(self):
		super()
		self.css      = read_resource('index.css')
		self.js       = read_resource('recaptcha.js')
		self.htmlbase = read_resource('recaptcha.html')

	def get_sitekey(self, req: CaptchaRequest) -> str:
		try:
			sitekey = req['options']['sitekey']
		except KeyError:
			return self.fallback_sitekey
		if isinstance(sitekey, str):
			return sitekey
		else:
			raise CaptchaException('options.sitekey must be a string')

	def is_invisible(self, req: CaptchaRequest) -> bool:
		try:
			invisible = req['options']['invisible']
		except KeyError:
			return False
		if isinstance(invisible, bool):
			return invisible
		else:
			raise CaptchaException('options.invisible must be a boolean')

	def generate(self, req: CaptchaRequest) -> str:
		options = {'data-sitekey': self.get_sitekey(req)}
		if self.is_invisible(req):
			options['data-size'] = 'invisible'
		return self.htmlbase.format(
			css    =self.css,
			js     =self.js,
			options=self.xml_attrs(options),
		)


class DeCaptcha:
	"""
	.. |CAPTCHA loop| image:: ../captcha-display-loop.svg
	"""

	logger = logging.getLogger('DeCaptcha')

	@classmethod
	def _on_load_failed(cls, *args):
		cls.logger.error('loading %s failed: %r', args[2], args)

	def __init__(self, html_generator: HTMLGenerator):
		self.html_generator   = html_generator # type: Final[HTMLGenerator]
		self._async_loop      = None # type: Optional[asyncio.AbstractEventLoop]
		self._window          = None # type: Optional[gtk.Window]
		self._webview         = None # type: Optional[webkit.WebView]
		self._requests        = []   # type: List[RequestTuple]
		self._current_request = None # type: Optional[RequestTuple]

	def _create_window(self):
		"""
		Create GTK window with a WebKit webview, add the necessary signal
		handlers, and set the User-Agent with youtube-dl.utils.random_user_agent
		if available.
		"""
		self.logger.debug('create new WebKit window')

		self._window = gtk.Window(title='webkitgtk')
		self._window.resize(1280, 720)
		self._window.set_position(gtk.WindowPosition.CENTER)
		self._window.set_accept_focus(False)
		self._window.connect('delete-event', self._on_window_closed)

		scroll = gtk.ScrolledWindow()
		self._window.add(scroll)

		self._webview = webkit.WebView()
		self._webview.connect('load-failed', self._on_load_failed)

		props = self._webview.get_settings().props
		props.enable_developer_extras = True
		ua = random_user_agent()
		if ua:
			props.user_agent = ua

		content_manager = self._webview.get_user_content_manager()
		content_manager.connect('script-message-received::decaptcha', self._on_script_message)
		content_manager.register_script_message_handler('decaptcha')

		scroll.add(self._webview)

		self._window.show_all()

	def _on_script_message(self, content_manager, message: webkit.JavascriptResult) -> None:
		"""
		Resolve current CAPTCHA with the message sent from inside the webview.

		Process next queued CAPTCHA.
		"""
		try:
			response = json.loads(message.get_js_value().to_json(0))
		except:
			self.logger.exception('cannot parse javascript message: %r', message)
			return
		if self._current_request is None:
			self.logger.warning('CAPTCHA response received, but no request currently processed')
		else:
			self._current_request.set_result({'response': response})
			self._current_request = None
		self._try_show_captcha()

	def _on_window_closed(self, widget, event):
		"""
		Cancel current CAPTCHA if possible.

		Process next queued CAPTCHA.
		"""
		self.logger.debug('Webkit window closed')
		if self._current_request:
			self._current_request.set_exception(CaptchaException('WebKit window closed by user'))
			self._current_request = None
		self._window  = None
		self._webview = None
		self._try_show_captcha()

	def _close(self):
		"""
		Close the WebKit window without calling _on_window_closed and
		subsequentially cancelling the current CAPTCHA.
		"""
		self._window.destroy()
		self._window  = None
		self._webview = None

	def _show_current_captcha(self):
		"""
		Display the current CAPTCHA. If the WebKit window is closed, open a new
		one.
		"""
		self.logger.info('processing request %r', self._current_request.request)
		html = self.html_generator.generate(self._current_request.request)
		if not self._window or not self._webview:
			self._create_window()
		self._webview.load_html(html, self._current_request.request['url'])

	def _try_show_current_captcha(self):
		"""
		Display the current CAPTCHA if set, otherwise start the CAPTCHA loop.
		"""
		if self._current_request is not None:
			self._show_current_captcha()
		else:
			self._try_show_captcha()

	def _try_show_captcha(self):
		"""
		If a CAPTCHA is currently being processed do nothing.

		If no more CAPTCHAs are queued close WebKit window.

		Otherwise start processing a new CAPTCHA.
		"""
		if self._current_request is not None:
			self.logger.debug('request processing loop already running')
		elif not self._requests:
			if self._window:
				self.logger.debug('no more requests queued, close WebKit window')
				self._close()
			else:
				self.logger.debug('no requests queued, WebKit window already closed')
		else:
			self._current_request = self._requests.pop(0)
			try:
				self._show_current_captcha()
				return
			except Exception as e:
				self.logger.exception('error displaying the CAPTCHA')
				self._current_request.set_exception(e)
				self._current_request = None
			self.logger.info('skipping current request')
			self._try_show_captcha()

	def run(self, loop=None, executor=None) -> Awaitable[None]:
		"""
		Safe to call from another thread.

		Start the GUI loop and start displaying CAPTCHAs.

		:param loop:     event loop to use, syncio.get_running_loop() if None
		:param executor: executor to use, default executor if None
		:returns:        a future that resolves when the GUI loop ends
		"""
		def proc():
			self.logger.debug('GUI loop starting...')
			gtk.main()
			# GUI loop done
			self._async_loop = None
			self.logger.debug('GUI loop finished')

		self._async_loop = loop or asyncio.get_running_loop()
		fut = self._async_loop.run_in_executor(executor, proc)
		glib.idle_add(self._try_show_current_captcha) # start event loop on start
		return fut

	def stop(self) -> None:
		"""
		Schedule glib callback that closes the window and stops the GUI loop.
		"""
		@glib.idle_add
		def _():
			if self._window:
				self._close()
			gtk.main_quit()

	def solve(self, req: CaptchaRequest) -> Awaitable[CaptchaSuccess]:
		"""
		Queue the CaptchaRequest for display in the WebKit window.

		:returns: a future that is done when the CAPTCHA was displayed and
		          solved or cancelled by the user
		"""
		if self._async_loop is None:
			raise RuntimeError('GUI loop is not started')
		fut = self._async_loop.create_future()
		@glib.idle_add
		def _():
			self.logger.debug('queueing CAPTCHA request %r...', req)
			self._requests.append(RequestTuple(
				req,
				lambda ret: self._async_loop.call_soon_threadsafe(fut.set_result,    ret),
				lambda e:   self._async_loop.call_soon_threadsafe(fut.set_exception, e),
			))
			self._try_show_captcha() # start event loop if necessary
		return fut

	def cancel_current(self) -> None:
		"""
		Cancel the CAPTCHA currently displayed in the WebKit window.
		"""
		@glib.idle_add
		def _():
			if self._current_request is None:
				self.logger.debug('no CAPTCHA request to cancel')
			else:
				self.logger.debug('canceling CAPTCHA request %r', self._current_request)
				self._current_request.set_exception(CaptchaException('# TODO #'))
				self._current_request = None
			self._try_show_captcha()
