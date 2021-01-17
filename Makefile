# Copyright (C) 2021 schnusch
#
# This file is part of decaptcha.
#
# decaptcha is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# decaptcha is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with decaptcha.  If not, see <https://www.gnu.org/licenses/>.

tsc = node_modules/.bin/tsc
browserify = node_modules/.bin/browserify
ts_files = \
	app/main.ts \
	app/util.ts \
	app/hosts.ts \
	$(wildcard app/hosts/*.ts)

gencert = mkdir -p $(@D) && openssl req -x509 -sha256 -nodes -days 365 \
	-newkey rsa:4096 -keyout $(@D)/private.key -out $(@D)/certificate.crt \
	-subj '/CN=localhost' || { $(RM) -r $(@D); false; }

all: dist/main.js public.mk ## build decaptcha
	$(MAKE) -f public.mk all
public.mk: genmake.sh
	TSC=$(tsc) ./genmake.sh > $@ || { $(RM) $@; false; }

dist/main.js: $(ts_files) tsconfig/node.json package-lock.json
	$(tsc) -p tsconfig/node.json

package-lock.json: package.json
	npm install

help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' Makefile \
	| sed -n 's/^\(.*\): \(.*\)## \(.*\)/\x1b[33m\1\x1b[39m\t\3/p' \
	| column -t -s '	'

run: all cert ## run decaptcha with self-signed certificates
	req='{"url":"https://decaptcha.test/","options":{"sitekey":"6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"}}'; \
	{ echo "$$req"; echo "$$req"; } | \
	bin/decaptcha --cert=dist/cert/certificate.crt --key=dist/cert/private.key --dev-tools

cert: dist/cert/certificate.crt dist/cert/private.key ## generate self-signed certificates
dist/cert/certificate.crt:
	$(gencert)
dist/cert/private.key:
	$(gencert)

clean: ## remove build artifacts
	$(RM) public.mk -r dist
distclean: clean ## remove build artifacts and downloaded libraries
	$(RM) package-lock.json -r node_modules
