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

/// <reference types="@types/grecaptcha"/>

async function postResponse(data: any): Promise<void> {
	const resp = await fetch('/captcha-response', {
		method:  'POST',
		headers: {'Content-Type': 'application/json'},
		body:    JSON.stringify({response: data}),
		mode:           'same-origin',
		credentials:    'omit',
		referrerPolicy: 'no-referrer',
	})
	if(!resp.ok) {
		const text = await resp.text()
		throw new Error("cannot send CAPTCHA response: " + text)
	}
}

function grecaptchaOnLoad(): void {
	grecaptcha.execute()
}

async function grecaptchaOnSubmit(): Promise<void> {
	const resp = grecaptcha.getResponse()

	const main    = <HTMLElement|null>document.querySelector('#main')
	const captcha = <HTMLElement|null>document.querySelector('.g-recaptcha')
	if(!main) {
		throw new Error("cannot find main div")
	} else if(!captcha) {
		throw new Error("cannot find CAPTCHA container")
	}

	const txt = main.appendChild(document.createElement('textarea'))
	txt.setAttribute('readonly', 'yes')
	txt.appendChild(document.createTextNode(resp))
	captcha.style.display = 'none'
	await postResponse(resp)
}
