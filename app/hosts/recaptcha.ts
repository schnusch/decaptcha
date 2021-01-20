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

import * as fs from 'fs'
import { IncomingMessage, ServerResponse } from 'http'
import * as jsonschema from 'jsonschema'
import * as path from 'path'

import { CaptchaHost, escapeXML, serveStaticFile } from './common'
import { CaptchaHostOptions, httpErrorPage } from '../util'

type ReCaptchaHostOptionsOptional = {
	sitekey?:   string,
	invisible?: boolean,
}
type ReCaptchaHostOptions = ReCaptchaHostOptionsOptional & {
	sitekey: string,
}
type AllReCaptchaHostOptions = {[host: string]: ReCaptchaHostOptions}

function processSiteKeys(data: {[host: string]: string | ReCaptchaHostOptions}): AllReCaptchaHostOptions {
	const processed: AllReCaptchaHostOptions = {}
	for(const host of Object.keys(data)) {
		if(!Object.prototype.hasOwnProperty.call(processed, host)) {
			const options = data[host] == 'string'
				? {sitekey: data[host] as string}
				: data[host] as ReCaptchaHostOptions
			options.invisible = options.invisible || false

			const hosts = (options as any).hosts || []
			delete (options as any).hosts
			if(hosts.indexOf(host) < 0) {
				hosts.push(host)
			}

			for(const host of hosts) {
				processed[host] = options
			}
		}
	}
	return processed
}

/**
 * this should probably be done asynchronously but that's not possible in the
 * constructor
 */
function loadSiteKeys(): AllReCaptchaHostOptions {
	const file = path.join(__dirname, '../recaptcha-sitekeys.json')
	const data = fs.readFileSync(file, {encoding: 'utf8'})
	return processSiteKeys(JSON.parse(data))
}

function findHost(
	hostOptions: AllReCaptchaHostOptions,
	givenHost:   string,
): ReCaptchaHostOptions | null {
	const hostParts = givenHost.split('.')
	while(hostParts.length > 0) {
		const host = hostParts.join('.')
		if(Object.prototype.hasOwnProperty.call(hostOptions, host)) {
			return hostOptions[host]
		}
		hostParts.shift()
	}
	return null
}

export class ReCaptcha extends CaptchaHost {
	private          currentOptions: ReCaptchaHostOptionsOptional
	private readonly defaultOptions: ReCaptchaHostOptionsOptional
	private readonly hostOptions:    AllReCaptchaHostOptions
	private          html:           string

	constructor(options?: ReCaptchaHostOptionsOptional) {
		super()
		this.currentOptions = { sitekey: undefined, invisible: undefined }
		this.defaultOptions = options || {}
		this.hostOptions    = options ? {} : loadSiteKeys()
		this.html           = ''
	}

	matchHost(host: string): boolean {
		return findHost(this.hostOptions, host) != null
	}

	private getOptions(host?: string): ReCaptchaHostOptions {
		const opts: ReCaptchaHostOptionsOptional = {
			sitekey:   this.currentOptions.sitekey,
			invisible: this.currentOptions.invisible,
		}
		if(opts.sitekey == undefined) {
			opts.sitekey = this.defaultOptions.sitekey
		}
		if(opts.invisible == undefined) {
			opts.invisible = this.defaultOptions.invisible
		}
		if(opts.sitekey == undefined || opts.invisible == undefined) {
			const hostOpts = host == undefined
				? null
				: findHost(this.hostOptions, host)
			if(hostOpts) {
				if(opts.sitekey == undefined) {
					opts.sitekey = hostOpts.sitekey
				}
				if(opts.invisible == undefined) {
					opts.invisible = hostOpts.invisible
				}
			}
		}
		if(opts.sitekey == undefined) {
			throw new Error(`cannot find sitekey for ${host || '<none>'}`)
		}
		return opts as ReCaptchaHostOptions
	}

	setOptions(options: CaptchaHostOptions) {
		jsonschema.validate(options, {
			type: 'object',
			properties: {
				sitekey:   {type: 'string'},
				invisible: {type: 'boolean'},
			},
		}, {
			allowUnknownAttributes: true,
			throwFirst:             true,
		})
		this.currentOptions = {
			sitekey:   options.sitekey   as string  | undefined,
			invisible: options.invisible as boolean | undefined,
		}
	}

	async init(): Promise<void> {
		this.html = await this.readFile('recaptcha.html', {encoding: 'utf8'})
		this.addFile('',              this.serveHtml.bind(this))
		this.addFile('/recaptcha.js', serveStaticFile('recaptcha.js', 'text/javascript; charset=utf-8'))
	}

	private serveHtml(req: IncomingMessage, resp: ServerResponse): void {
		if(req.method != 'GET') {
			httpErrorPage(resp, 405, "only GET requests allowed")
			return
		}

		let host = req.headers['host']
		host = host && host.replace(/:\d+$/, '')
		const { invisible, sitekey } = this.getOptions(host)
		let recaptchaAttributes = `data-sitekey="${escapeXML(sitekey)}"`
		if(invisible) {
			recaptchaAttributes += ' data-size="invisible"'
		}
		const html = this.html.replace(/<!-- recaptcha config -->/, recaptchaAttributes)
		resp.writeHead(200, {'Content-Type': 'text/html; charset=utf-8'})
		resp.end(html, 'utf8')
	}
}
