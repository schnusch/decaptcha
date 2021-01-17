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

import { DecaptchaTest } from './hosts/decaptchatest'

export const captchaHosts: CaptchaHost[] = [
	new DecaptchaTest(),
]

import { CaptchaHost } from './hosts/common'

export function getHostHandler(host: string): CaptchaHost | null {
	for(const captchaHost of captchaHosts) {
		if(captchaHost.matchHost(host)) {
			return captchaHost
		}
	}
	return null
}
