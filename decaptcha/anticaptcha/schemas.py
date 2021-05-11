def _update(a, b, *args):
	""" Recursively update dicts and join lists like sets. """
	if args:
		b = _update(b, *args)
	if isinstance(a, dict) and isinstance(b, dict):
		c = {}
		c.update(a)
		for battr, bval in b.items():
			try:
				aval = c[battr]
			except KeyError:
				c[battr] = bval
			else:
				c[battr] = _update(aval, bval)
		return c
	elif isinstance(a, list) and isinstance(b, list):
		return list(set(a) | set(b))
	elif isinstance(a, str) and isinstance(b, str):
		return b
	else:
		raise ValueError('cannot merge %r and %r' % (type(a), type(b)))

HCaptchaTaskProxyless = {
	'type': 'object',
	'properties': {
		'type':       {'const': 'HCaptchaTaskProxyless'},
		'websiteURL': {'type': 'string'},
		'websiteKey': {'type': 'string'},
	},
	'required': [
		'type',
		'websiteURL',
		'websiteKey',
	],
}

HCaptchaTask = _update(HCaptchaTaskProxyless, {
	'properties': {
		'type':          {'const': 'HCaptchaTask'},
		'proxyType':     {'enum': ['http', 'https', 'socks4', 'socks5']},
		'proxyAddress':  {'type': 'string'},
		'proxyPort':     {'type': 'integer'},
		'userAgent':     {'type': 'string'},
		# optional
		'proxyLogin':    {'type': 'string'},
		'proxyPassword': {'type': 'string'},
		'cookies':       {'type': 'string'},
	},
	'required': [
		'proxyType',
		'proxyAddress',
		'proxyPort',
		'userAgent',
	],
})

RecaptchaV2TaskProxyless = _update(HCaptchaTaskProxyless, {
	'properties': {
		'type': {'const': 'RecaptchaV2TaskProxyless'},
		# optional
		'websiteSToken':       {'type': 'string'},
		'recaptchaDataSValue': {'type': 'string'},
		'isInvisible':         {'type': 'string'},
	},
})

RecaptchaV2Task = _update(HCaptchaTask, RecaptchaV2TaskProxyless, {
	'properties': {
		'type': {'const': 'RecaptchaV2Task'},
	},
})

createTask = {
	'type': 'object',
	'properties': {
		'task': {
			'anyOf': [
				HCaptchaTaskProxyless,
				HCaptchaTask,
				RecaptchaV2TaskProxyless,
				RecaptchaV2Task,
			],
		},
		'callbackUrl': {
			'type': 'string',
		},
	},
	'required': ['task'],
	'additionalProperties': True,  # ignore other properties
}

getTaskResult = {
	'type': 'object',
	'properties': {
		'taskId': {'type': 'string'},
	},
	'required': ['taskId'],
	'additionalProperties': True,  # ignore other properties
}

all = {
	'HCaptchaTaskProxyless':    HCaptchaTaskProxyless,
	'HCaptchaTask':             HCaptchaTask,
	'RecaptchaV2TaskProxyless': RecaptchaV2TaskProxyless,
	'RecaptchaV2Task':          RecaptchaV2Task,
	'createTask':               createTask,
	'getTaskResult':            getTaskResult,
}
