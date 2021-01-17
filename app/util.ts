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
import { STATUS_CODES, IncomingMessage, ServerResponse } from 'http'
import * as jsonschema from 'jsonschema'
import { AddressInfo } from 'net'
import * as path from 'path'
import * as stream from 'stream'
import { promisify } from 'util'

export type Json = null
	| boolean
	| number
	| string
	| Json[]
	| JsonObject
export type JsonObject = {[key: string]: Json}

export type CaptchaHostOptions = JsonObject

export type CaptchaRequest = {
	type?:    string
	url:      string
	options?: CaptchaHostOptions
}
const captchaRequestSchema: jsonschema.Schema = {
	type: 'object',
	required: ['url'],
	properties: {
		url:     {type: 'string'},
		type:    {type: 'string'},
		options: {type: 'object'},
	},
}

export type CaptchaSuccess = {
	error?:   false
	response: string
}
const captchaSuccessSchema: jsonschema.Schema = {
	type: 'object',
	required: ['response'],
	properties: {
		error:    {type: 'boolean'},
		response: {type: 'any'},
	},
}

export type CaptchaError = {
	error:  true
	reason: string
}

export type CaptchaResponse = CaptchaSuccess | CaptchaError

const jsonschemaOptions = {
	allowUnknownAttributes: true,
	throwFirst:             true,
}

export function parseCaptchaRequest(data: string): CaptchaRequest {
	const req = JSON.parse(data)
	jsonschema.validate(req, captchaRequestSchema, jsonschemaOptions)
	return req as CaptchaRequest
}

export function parseCaptchaSuccess(data: string): CaptchaSuccess {
	const resp = JSON.parse(data)
	jsonschema.validate(resp, captchaSuccessSchema, jsonschemaOptions)
	return resp as CaptchaSuccess
}

export function URLfromAddressInfo(addr: AddressInfo, scheme?: string): string {
	let url = addr.family == 'IPv6' ? `[${addr.address}]` : addr.address
	url += `:${addr.port}`
	if(scheme) {
		url = `${scheme}://${url}`
	}
	return url
}

function openFile(name: string, options?: any): Promise<stream.Readable> {
	return new Promise<stream.Readable>((resolve, reject) => {
		const stream = fs.createReadStream(name, options)
		stream.once('readable', () => resolve(stream))
		stream.once('error', error => reject(error))
	})
}

export async function openPublicFile(name: string, options?: any): Promise<stream.Readable> {
	let error: Error = new Error("no public directories")
	for(const dir of getPublicDirectories()) {
		try {
			return await openFile(path.join(dir, name), options)
		} catch(e) {
			error = e
		}
	}
	throw error
}

export function readAll(stream: stream.Readable): Promise<string> {
	return new Promise<string>((resolve, reject) => {
		let data = ''
		stream.once('error', (e: Error) => reject(e))
		stream.on('data', (chunk: string) => { data += chunk })
		stream.once('end',  () => resolve(data))
	})
}

export const immediate = () => new Promise<void>((resolve, _reject) => setImmediate(resolve))

export const readFile = promisify(fs.readFile)

export function getPublicDirectories(): string[] {
	// TODO something with environment variables
	return [
		path.join(__dirname, '../dist/public'),
	]
}

export function httpErrorPage(resp: ServerResponse, code: number, msg?: string): void {
	let body = STATUS_CODES.hasOwnProperty(code)
		? `${code} ${STATUS_CODES[code]}`
		: `HTTP error ${code}`
	if(msg) {
		body += "\n\n" + msg
	}
	resp.writeHead(code, {'Content-Type': 'text/plain; charset=utf-8'})
	resp.end(body + "\n", 'utf8')
}
