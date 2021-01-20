# decaptcha

This tool lets you solve [reCAPTCHAs](https://developers.google.com/recaptcha/intro)
(or other CAPTCHAs) outside the browser.

To solve CAPTCHAs you have to communicate with the stdin/stdout of the process.
Write [CaptchaRequest](https://github.com/schnusch/decaptcha/blob/a376080/app/util.ts#L38)s
encoded to a single line of JSON to stdin. The CAPTCHA responses are written to
the process's stdout.

## About

Because reCAPTCHA verifies the host it is running on, reCAPTCHAs from a site
cannot simply be embedded somewehere else with code extracting the reCAPTCHA
challenge response around them. The page extracting the reCAPTCHA challenge
response must be served on the original host. [[1]](https://developers.google.com/recaptcha/docs/domain_validation "Domain/Package Name Validation")

To imitate this the following steps are taken:

 1. A local HTTPS server with any certificate is started. That server serves
    our pages that can embed the CAPTCHA and extract the CAPTCHA response.

 2. A local SOCKS5 proxy is started that allows us to hijack connections to
    the original host. Any connection request to the host, whose CAPTCHA we want
    solved, is redirected to our local HTTPS server. SOCKS5 allows the
    connection by hostname (and electron/Google Chrome seems to do so by
    default) so no DNS lookup is needed and requests to the host can easily be
    detected.

 3. An electron BrowserWindow is started that uses our local SOCKS5 proxy. Then
    the site we want to solve the CAPTCHA on is opened. This request is
    hijacked by our SOCKS5 proxy and actually served by our HTTPS server. So our
    pages, that get the CAPTCHA challenge response and pass it on to the
    application, can be served.

## "Installation"

  * To build the project run

    ```sh
    make all
    ```

    now everything needed to run should be in `dist/` or `bin/`.

  * To show available make targets run

    ```sh
    make help
    ```

  * To run with a self-signed certificate

    ```sh
    make run
    ```

## Usage

**Usage:** decaptcha --cert=*CERT* --key=*KEY* [--https-port=*PORT*] [--dev-tools] [--close-window]

First you have to have a SSL certificate and its key. It can be self-signed, it
is only used for our HTTPS server and will be blindy accepted by our electron
app.

To solve CAPTCHAS with decaptcha you have to communicate with it on its stdin
and stdout. An example CAPTCHA requests looks like this:

```json
{
	"url": "https://decaptcha.test/anypathyoulike",
	"options": {
		"sitekey": "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI",
		"invisible": false
	}
}
```

This request has to be JSON encoded and must only consist of a single line.

decaptcha will add the CAPTCHA request to its queue and open a window to display
the CAPTCHAs.

The corresponding CAPTCHA response will be a single line of JSON written to
stdout and will look like this:

```json
{
	"response": "..."
}
```

or

```json
{
	error: true,
	reason: "cancelled by closing the window"
}
```

if an error occured.

## Limitations

  * Only hosts for which a handler is created (see [app/hosts/](https://github.com/schnusch/decaptcha/tree/master/app/hosts))
    are supported, but there exists a generic handler for reCAPTCHA that uses a
    site key provided in the CAPTCHA request or from [a repository of reCAPTCHA
    site keys](https://github.com/schnusch/recaptcha-sitekeys/).

  * Plain unencrypted HTTP will not work because we are only running a HTTP**S**
    server, but this should not be too big of a problem.

## But why electron? I only have so much RAM.

The way the web is going a probably full-featured web browser is needed to solve
reCAPTCHA anyway. Furthermore `Object.defineProperty` does not work on
`window.location` in modern browsers anymore (because `window`'s and
`window.location`'s properties are non-configurable) so we cannot simply fake
our pages running on our target host. Also [Selenium](https://www.selenium.dev/documentation/en/webdriver/ "Selenium WebDriver")
does not seem to have support for custom certificates like electron's
[`certificate-error`](https://www.electronjs.org/docs/api/app#event-certificate-error).
WebExtension do not seem to have the ability to [override certificate
verification decisions](https://bugzilla.mozilla.org/show_bug.cgi?id=1435951)
and Extracting the CAPTCHA response from the original page will be difficult,
because some sites are heavily obfuscated.
