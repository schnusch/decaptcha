"use strict";
function postResponse(data) {
	webkit.messageHandlers.decaptcha.postMessage(data);
}

function onLoad() {
	grecaptcha.execute();
}

function onSubmit() {
	const resp = grecaptcha.getResponse();

	const main    = document.querySelector('#main');
	const captcha = main.firstElementChild;

	const txt = main.appendChild(document.createElement('textarea'));
	txt.setAttribute('readonly', 'yes');
	txt.appendChild(document.createTextNode(resp));
	captcha.style.display = 'none';
	postResponse(resp);
}
