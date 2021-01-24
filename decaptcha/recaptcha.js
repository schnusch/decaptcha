"use strict";
function postResponse(data) {
	webkit.messageHandlers.decaptcha.postMessage(data);
}

function grecaptchaOnLoad() {
	grecaptcha.execute();
}

function grecaptchaOnSubmit() {
	const resp = grecaptcha.getResponse();

	const main    = document.querySelector('#main');
	const captcha = document.querySelector('.g-recaptcha');

	const txt = main.appendChild(document.createElement('textarea'));
	txt.setAttribute('readonly', 'yes');
	txt.appendChild(document.createTextNode(resp));
	captcha.style.display = 'none';
	postResponse(resp);
}
