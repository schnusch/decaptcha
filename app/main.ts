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

import { app, App, BrowserWindow, Certificate, Event, WebContents } from 'electron'
import { EventEmitter } from 'events'
import { IncomingMessage, ServerResponse } from 'http'
import * as https from 'https'
import { AddressInfo } from 'net'
import * as socksv5 from 'socksv5'

import yargs from 'yargs'
// import hideBin like this
//     import { hideBin } from 'yargs/helpers'
// yields following error
//     Could not find a declaration file for module 'yargs/helpers'.
//     ... implicitly has an 'any' type.
// so we do it this way:
const { hideBin } = require('yargs/helpers')

import {
	CaptchaError,
	CaptchaHostOptions,
	CaptchaRequest,
	CaptchaResponse,
	CaptchaSuccess,
	httpErrorPage,
	immediate,
	parseCaptchaRequest,
	parseCaptchaSuccess,
	readAll,
	readFile,
	URLfromAddressInfo,
} from './util'
import { CaptchaHost } from './hosts/common'
import { getHostHandler } from './hosts'

type CommandLineArgs = {
	cert:          string,
	key:           string,
	'https-port'?: number,
	'dev-tools'?:  boolean,
}

function parseCommandLine(): CommandLineArgs {
	const usage = "Usage: $0 --cert=CERT --key=KEY [--https-port=PORT] [--dev-tools]"
	const { argv } = yargs(hideBin(process.argv))
		.wrap(yargs.terminalWidth())
		.scriptName('decaptcha') // on $0 detection cannot be relied
		.usage(usage)
		.options({
			'cert': {
				type:         'string',
				requiresArg:  true,
				demandOption: true,
				description:  "path to SSL certificate",
			},
			'key': {
				type:         'string',
				requiresArg:  true,
				demandOption: true,
				description:  "path to SSL private key",
			},
			'https-port': {
				type:        'number',
				requiresArg: true,
				description: "port for the HTTPS server to listen on and redirect connections to",
			},
			'dev-tools': {
				type:        'boolean',
				description: "open Chrome DevTools",
			},
		})
		.alias('version', 'V')
	const httpsPort = argv['https-port']
	if(Number.isNaN(httpsPort) || httpsPort && (httpsPort < 0 || 65553 < httpsPort)) {
		console.error(`${argv['$0']}: argument for option --https-port must be in the range 0-65535, not`, argv['https-port'])
		process.exit(1)
	} else if(argv._.length > 0) {
		console.error(`${argv['$0']}: unexpected arguments:`, argv._, "\n")
		console.error(usage)
		process.exit(1)
	}
	return argv
}

interface Hijacker {
//	matchHost(addr: AddressInfo): Promise<AddressInfo>
}

interface CaptchaServer {
	on(event: 'response', callback: (resp: CaptchaSuccess) => void): this
}
class CaptchaServer extends EventEmitter implements Hijacker {
	private readonly port:  number
	public  readonly cert:  string
	private          host:  CaptchaHost | null
	private readonly https: https.Server

	constructor({port, cert, key}: {port?: number, cert: string, key: string}) {
		super()
		this.port  = port || 0
		this.cert  = cert
		this.host  = null
		this.https = https.createServer({
			cert: this.cert,
			key:  key,
		}, this.listener.bind(this))
	}

	private async listener(req: IncomingMessage, resp: ServerResponse): Promise<void> {
		if(!this.host) {
			httpErrorPage(resp, 503, "no host set")
			return
		}
		const path = (req.url || '/').replace(/[?#].*$/, '')
		if(path == this.host.getResponseEndpoint()) {
			if(req.method == 'POST') {
				try {
					const text = await readAll(req)
					this.emit('response', parseCaptchaSuccess(text))
				} catch(e) {
					console.error("cannot parse CaptchaSuccess:", e)
					httpErrorPage(resp, 500, `cannot parse CaptchaSuccess: ${e}`)
				}
			} else {
				httpErrorPage(resp, 405, "only POST requests allowed")
			}
		} else {
			try {
				await this.host.serveRequest(req, resp)
			} catch(error) {
				httpErrorPage(resp, 404, `current host ${this.host && this.host.constructor.name} does not serve ${path}`)
			}
		}
	}

	address(): AddressInfo {
		const addr = this.https.address()
		if(!addr) {
			throw new Error("cannot get HTTPS server address")
		}
		return addr as AddressInfo
	}

	get listening(): boolean {
		return this.https.listening
	}

	listen(): Promise<void> {
		return new Promise<void>((resolve, reject) => {
			this.https.listen(this.port, 'localhost', () => {
				if(this.listening) {
					resolve()
				} else {
					reject(new Error("HTTPS server cannot start listening"))
				}
			})
		})
	}

	stop(): void {
		// TODO
		throw new Error("Not Implemented")
	}

	setHost(host: CaptchaHost | null) {
		console.error(`CatpchaHost.setHost(${host && host.constructor.name})`)
		this.host = host
	}
}

type HijackCondition = (addr: {address: string, port: number}) => boolean

class HijackingSocksProxy extends socksv5.Server {
	private condition: HijackCondition

	constructor(readonly destination: {address: string, port: number}) {
		super()
		this.condition = _ => true
		this.useAuth(socksv5.auth.None())
		this.on('connection', this.listener.bind(this))
	}

	private listener(info: socksv5.RequestInfo, accept: () => void, deny: () => void): void {
		// we don't really need anything else
		if(info.cmd != 'connect') {
			deny()
			return
		}
		// let's just hope that info.dstAddr is a hostname,
		// elecron/Google Chrome seems to do so by default
		if(!this.condition || this.condition({address: info.dstAddr, port: info.dstPort})) {
			// hijack connection
//			console.error(`hijacking connection to ${info.dstAddr}:${info.dstPort}`)
			info.dstAddr = this.destination.address
			info.dstPort = this.destination.port
		}
		accept()
	}

	listen(): Promise<void> {
		return new Promise<void>((resolve, reject) => {
			super.listen(0, 'localhost', () => {
				if(this._srv.listening) {
					resolve()
				} else {
					reject(new Error("SOCKS server cannot start listening"))
				}
			})
		})
	}

	address(): AddressInfo {
		const addr = super.address()
		if(!addr) {
			throw new Error("cannot get SOCKS server address")
		}
		return addr as AddressInfo
	}

	setHost(host: CaptchaHost | null) {
		console.error(`HijackingSocksProxy.setHost(${host && host.constructor.name})`)
		if(host) {
			this.condition = ({address}) => host.matchHost(address)
		} else {
			this.condition = _ => true
		}
	}
}

type CaptchaRequestWithCallbacks = {
	request: CaptchaRequest,
	resolve: (resp: CaptchaSuccess) => void,
	reject:  (e:    Error)          => void,
}

class DeCaptcha extends EventEmitter {
	private window:         BrowserWindow | null
	private captchas:       CaptchaRequestWithCallbacks[]
	private currentCaptcha: CaptchaRequestWithCallbacks | null

	constructor(
		private app:           App,
		private captchaServer: CaptchaServer,
		private socksProxy:    HijackingSocksProxy,
		private openDevTools:  boolean             = false,
	) {
		super()
		this.window         = null
		this.captchas       = []
		this.currentCaptcha = null

		this.captchaServer.on('response', async (resp: CaptchaSuccess) => {
			if(this.currentCaptcha) {
				this.currentCaptcha.resolve(resp)
				this.currentCaptcha = null
			} else {
				throw new Error("unexpected response: " + JSON.stringify(resp))
			}

			await immediate() // not really necessary but makes logging prettier
			this.nextCaptcha()
		})

		// accept our self-signed certificate
		this.app.on('certificate-error', (
			event:        Event,
			_webContents: WebContents,
			_url:         string,
			_error:       string,
			errorCert:    Certificate,
			callback:     (isTrusted: boolean) => void,
		): void => {
			if(errorCert.data == this.captchaServer.cert) {
				event.preventDefault()
				callback(true)
			} else {
				callback(false)
			}
		})
	}

	private async openWindow(): Promise<void> {
		console.error("opening new window...")

		this.window = new BrowserWindow({
			webPreferences: {
				contextIsolation: true,
				safeDialogs:      true,
				autoplayPolicy:   "user-gesture-required",

				// shouldn't be needed
				webgl:        false,
				enableWebSQL: false,
			},
		})
		// when listening for `closed` event, the window opened right after is
		// also closed, so we listen on `close`
		this.window.once("close", (_ev: Event) => {
			if(this.window) {
				// it actually seems to be the call to `destroy` that does this,
				// so we don't do this either
				//this.window.destroy()
				this.window = null
			}
			this.cancelCurrentCaptcha()
		})

		this.window.removeMenu()
		if(this.openDevTools) {
			this.window.webContents.openDevTools()
		}
		await this.window.webContents.session.setProxy({
			proxyRules: URLfromAddressInfo(this.socksProxy.address(), 'socks5'),
		})
	}

	private async getWindow(): Promise<BrowserWindow> {
		if(!this.window) {
			await this.openWindow()
			if(!this.window) {
				throw new Error("window was closed while opening")
			}
		}
		await this.window.webContents.session.clearStorageData()
		return this.window
	}

	cancelCurrentCaptcha(): void {
		if(!this.currentCaptcha) {
			return
		}
		console.error(`CAPTCHA ${this.currentCaptcha.request.url} canceled.`)
		this.currentCaptcha.reject(new Error("cancelled by closing the window"))
		this.currentCaptcha = null // done with current CAPTCHA
		this.nextCaptcha()
	}

	private async nextCaptcha(): Promise<void> {
		if(this.currentCaptcha) {
			return
		}

		this.currentCaptcha = this.captchas.shift() || null
		if(!this.currentCaptcha) {
			console.error("no CAPTCHAs pending, closing window...")
			this.window?.destroy()
			this.window = null
			return
		}

		console.error("\nprocessing next CAPTCHA", this.currentCaptcha.request)
		const url  = new URL(this.currentCaptcha.request.url)
		const host = getHostHandler(url.hostname)
		if(host) {
			host.setOptions(this.currentCaptcha.request.options || {})
			await host.init()
		}
		this.captchaServer.setHost(host)
		this.socksProxy.setHost(host)

		console.error(`displaying CAPTCHA ${this.currentCaptcha.request.url} ...`)
		const win = await this.getWindow()
		if(!this.currentCaptcha) {
			throw new Error("currentCaptcha is null")
		}
		win.loadURL(this.currentCaptcha.request.url)
	}

	/**
	 * TODO documentation
	 * always resolves, maybe do this in a sub-class
	 */
	solve(req: CaptchaRequest): Promise<CaptchaResponse> {
		return new Promise<CaptchaSuccess>(async (resolve, reject) => {
			// just queue up the request
			this.captchas.push({
				request: req,
				resolve: resolve,
				reject:  reject,
			})
			// (re-)start handling requests
			this.nextCaptcha()
		}).catch(error => {
			// send error response
			console.error("CAPTCHA error", req.url, error)
			return {
				error:  true,
				reason: error.message,
			} as CaptchaError
		})
	}
}

async function main(): Promise<void> {
	process.stderr.setEncoding('utf8')

	const opts = parseCommandLine()
	const [cert, key, _] = await Promise.all([
		readFile(opts.cert, {encoding: 'ascii'}),
		readFile(opts.key,  {encoding: 'ascii'}),
		app.whenReady(),
	])

	console.error("starting CAPTCHA server...")
	const captchaServer = new CaptchaServer({
		port: opts['https-port'],
		cert: cert,
		key:  key,
	})
	await captchaServer.listen()
	const httpsAddr = captchaServer.address()
	console.error("CAPTCHA server listening on", URLfromAddressInfo(httpsAddr, 'https'))

	console.error("starting hijacking SOCKS server...")
	const socksProxy = new HijackingSocksProxy({
		address: httpsAddr.address,
		port:    httpsAddr.port,
	})
	await socksProxy.listen()
	console.error("hijacking SOCKS proxy listening on", URLfromAddressInfo(socksProxy.address(), 'socks5'))

	const decaptcha = new DeCaptcha(app, captchaServer, socksProxy, opts['dev-tools'])

	const testReq: CaptchaRequest = {
		url: 'https://decaptcha.test/',
		options: {
			// test key, see https://developers.google.com/recaptcha/docs/faq#id-like-to-run-automated-tests-with-recaptcha.-what-should-i-do
			sitekey: '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
		}
	}
	const echoResp = (resp: CaptchaResponse) => {
		console.error("CAPTCHA response", resp)
	}

	decaptcha.solve(testReq).then(echoResp)
	decaptcha.solve(testReq).then(echoResp)
}
main()
