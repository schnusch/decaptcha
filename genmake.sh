#!/bin/sh
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

set -eu

TSC="${TSC:-node_modules/.bin/tsc}"
TSCONFIG="${TSCONFIG:-tsconfig/web.json}"

tsify() {
	set -- "$1" "${2%.ts}.js"
	echo "$2: $1 $TSCONFIG"
	echo "	$TSC -p $TSCONFIG"
	all=" $2$all" # prepend prerequisite
}

copy() {
	echo "$2: $1"
	echo "	install -Dm 644 $1 $2"
	all="$all $2" # append prerequisite
}

recurse() {
	if [ -d "$1" -a ! -L "$1" ]; then
		for f in "$1"/*; do
			# WARNING: $f will be overwritten in recursion
			recurse "$f" "$2/${f##*/}"
		done
	elif [ -z "${1%%*.ts}" -a ! -d "$1" ]; then
		tsify "$1" "$2"
	else
		copy "$1" "$2"
	fi
}

all=''
recurse app/public dist/public
echo "all:$all"
