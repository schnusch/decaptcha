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
import logging
import unittest

from decaptcha import (
	CaptchaException,
	DeCaptcha,
	HCaptchaHTMLGenerator,
	ReCaptchaHTMLGenerator,
)

class ReCaptcha(unittest.TestCase):
	def setUp(self):
		htmlgen     = ReCaptchaHTMLGenerator()
		self.viewer = DeCaptcha(htmlgen)
		self.gui    = None

	async def interrupt(self):
		await asyncio.sleep(3)
		logging.debug('stopping GUI for 2 seconds')
		self.viewer.stop()
		await self.gui
		await asyncio.sleep(2)
		self.gui = self.viewer.run()

	async def solve_captchas(self):
		self.gui = self.viewer.run()
		try:
			requests = [
				self.viewer.solve({
					'url': 'https://decaptcha.test/1',
					'options': {'invisible': True},
				}),
				self.viewer.solve({'url': 'https://decaptcha.test/2'}),
			]
			late_requests = [
				{'url': 'https://decaptcha.test/3', 'options': {'invisible': True}},
			]
			requests[-2].add_done_callback(lambda fut: requests.extend(map(self.viewer.solve, late_requests)))

			for awaitable in requests:
				try:
					print(await awaitable)
				except CaptchaException as e:
					print(e.to_dict())
				except:
					logging.exception('error solving CAPTCHA')

			self.viewer.html_generator = HCaptchaHTMLGenerator()
			try:
				print(await self.viewer.solve({
					'url': 'https://captcha.website/',
					'options': {
						'sitekey': '33f96e6a-38cd-421b-bb68-7806e1764460',
					},
				}))
			except CaptchaException as e:
				print(e.to_dict())
			except:
				logging.exception('error solving CAPTCHA')
		finally:
			self.viewer.stop()
		await self.gui

	async def atest_recaptcha(self):
		logging.basicConfig(
			format='[%(asctime)s] %(levelname)-8s %(name)-13s %(message)s',
			level=logging.DEBUG,
		)
		await asyncio.gather(
			self.interrupt(),
			self.solve_captchas(),
		)

	def test_recaptcha(self):
		asyncio.run(self.atest_recaptcha())
