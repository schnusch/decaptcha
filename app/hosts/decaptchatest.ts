/*!
 * Copyright (C) 2021 schnusch
 *
 * This file is part of decaptcha.
 *
 * decaptcha is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * decaptcha is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with decaptcha.  If not, see <https://www.gnu.org/licenses/>.
 */

import { ReCaptcha } from './recaptcha'

export class DecaptchaTest extends ReCaptcha {
	constructor() {
		super({
			// testing site key, see https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do
			sitekey:   '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI',
			invisible: true,
		})
	}

	matchHost(host: string): boolean {
		return host.match(/(^|\.)decaptcha\.test$/) != null
	}
}
