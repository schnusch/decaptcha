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

import { IncomingMessage, ServerResponse } from 'http'
import * as fs from 'fs'
import * as path from 'path'
import * as stream from 'stream'

import { CaptchaHostOptions, getPublicDirectories, httpErrorPage, openPublicFile, readAll, readFile } from '../util'

export type RequestHandler = (req: IncomingMessage, res: ServerResponse) => void

export function escapeXML(text: string): string {
	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/"/g, '&dquot;')
		.replace(/'/g, '&squot;')
	//"
}

export function serveStaticFile(path: string, mime: string): RequestHandler {
	return (req: IncomingMessage, resp: ServerResponse): void => {
		if(req.method != 'GET') {
			httpErrorPage(resp, 405, "only GET requests allowed")
		} else {
			openPublicFile(path, {encoding: 'utf8'})
				.then(file => {
					resp.writeHead(200, {'Content-Type': mime})
					file.pipe(resp)
				})
				.catch(error => {
					console.error(error)
					httpErrorPage(resp, error.code == 'ENOENT' ? 404 : 500, `${error}`)
				})
		}
	}
}

export function serveStaticBuffer(data: string, mime: string): RequestHandler {
	return (req: IncomingMessage, resp: ServerResponse): void => {
		if(req.method != 'GET') {
			httpErrorPage(resp, 405, "only GET requests allowed")
		} else {
			resp.writeHead(200, {'Content-Type': mime})
			resp.end(data, 'utf8')
		}
	}
}

export abstract class CaptchaHost {
	/**
	 * this should really be static, but I don't know how to make it overridable
	 */
	abstract matchHost(host: string): boolean

	/**
	 * again, should probably be static
	 */
	getResponseEndpoint(): string {
		return '/captcha-response'
	}

	private paths: {[path: string]: RequestHandler}

	constructor() {
		this.paths = {}
		this.addFile('/index.css', serveStaticFile('index.css', 'text/css; charset=utf-8'))
	}

	setOptions(_options: CaptchaHostOptions) { }

	async init(): Promise<void> { }

	protected addFile(path: string, handler: RequestHandler): void {
		this.paths[path] = handler
	}

	public serveRequest(req: IncomingMessage, resp: ServerResponse): Promise<void> {
		return new Promise<void>((resolve, reject) => {
			const path    = (req.url || '/').replace(/[?#].*$/, '')
			const handler = this.paths[path] || this.paths['']
			if(handler) {
				handler(req, resp)
				resolve()
			} else {
				reject()
			}
		})
	}

	protected async readFile(name: string, options?: any): Promise<string> {
		const stream = await openPublicFile(name, options)
		return await readAll(stream)
	}
}

export abstract class ReCaptchaHost extends CaptchaHost {
	protected sitekeyXML: string | null

	constructor() {
		super()
		this.sitekeyXML = null
	}

	// TODO matchHost, see https://developers.google.com/recaptcha/docs/domain_validation

	setOptions(options: CaptchaHostOptions) {
		if(!options.hasOwnProperty('sitekey')) {
			throw new Error("options is missing 'sitekey'")
		} else if(typeof options.sitekey != 'string') {
			throw new Error("options.sitekey must be a string")
		}
		this.sitekeyXML = escapeXML(options.sitekey)
	}

	async init(): Promise<void> {
		let html = await this.readFile('recaptcha.html', {encoding: 'utf8'})
		if(this.sitekeyXML) {
			html = html.replace(/<!-- sitekey xml -->/g, this.sitekeyXML)
		}
		this.addFile('',              serveStaticBuffer(html, 'text/html; charset=utf-8'))
		this.addFile('/recaptcha.js', serveStaticFile('recaptcha.js', 'text/javascript; charset=utf-8'))
	}
}
