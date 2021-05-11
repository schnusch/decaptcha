ERROR_KEY_DOES_NOT_EXIST = {
    'errorId': 1,
    'errorCode': 'ERROR_KEY_DOES_NOT_EXIST',
    'errorDescription': "Account authorization key not found in the system",
}

ERROR_NO_SLOT_AVAILABLE = {
    'errorId': 2,
    'errorCode': 'ERROR_NO_SLOT_AVAILABLE',
    'errorDescription': "No idle captcha workers are available at the moment, please try a bit later or try increasing your maximum bid here",
}

ERROR_ZERO_CAPTCHA_FILESIZE = {
    'errorId': 3,
    'errorCode': 'ERROR_ZERO_CAPTCHA_FILESIZE',
    'errorDescription': "The size of the captcha you are uploading is less than 100 bytes.",
}

ERROR_TOO_BIG_CAPTCHA_FILESIZE = {
    'errorId': 4,
    'errorCode': 'ERROR_TOO_BIG_CAPTCHA_FILESIZE',
    'errorDescription': "The size of the captcha you are uploading is more than 500,000 bytes.",
}

ERROR_ZERO_BALANCE = {
    'errorId': 10,
    'errorCode': 'ERROR_ZERO_BALANCE',
    'errorDescription': "Account has zeo or negative balance",
}

ERROR_IP_NOT_ALLOWED = {
    'errorId': 11,
    'errorCode': 'ERROR_IP_NOT_ALLOWED',
    'errorDescription': "Request with current account key is not allowed from your IP. Please refer to IP list section located here",
}

ERROR_CAPTCHA_UNSOLVABLE = {
    'errorId': 12,
    'errorCode': 'ERROR_CAPTCHA_UNSOLVABLE',
    'errorDescription': "Captcha could not be solved by 5 different workers",
}

ERROR_BAD_DUPLICATES = {
    'errorId': 13,
    'errorCode': 'ERROR_BAD_DUPLICATES',
    'errorDescription': "100% recognition feature did not work due to lack of amount of guess attempts",
}

ERROR_NO_SUCH_METHOD = {
    'errorId': 14,
    'errorCode': 'ERROR_NO_SUCH_METHOD',
    'errorDescription': "Request to API made with method which does not exist",
}

ERROR_IMAGE_TYPE_NOT_SUPPORTED = {
    'errorId': 15,
    'errorCode': 'ERROR_IMAGE_TYPE_NOT_SUPPORTED',
    'errorDescription': "Could not determine captcha file type by its exif header or image type is not supported. The only allowed formats are JPG, GIF, PNG",
}

ERROR_NO_SUCH_CAPCHA_ID = {
    'errorId': 16,
    'errorCode': 'ERROR_NO_SUCH_CAPCHA_ID',
    'errorDescription': "Captcha you are requesting does not exist in your current captchas list or has been expired.\nCaptchas are removed from API after 5 minutes after upload.\nReports for incorrect captchas accepted within 60 seconds after task completion by a worker.",
}

ERROR_EMPTY_COMMENT = {
    'errorId': 20,
    'errorCode': 'ERROR_EMPTY_COMMENT',
    'errorDescription': '"comment" property is required for this request',
}

ERROR_IP_BLOCKED = {
    'errorId': 21,
    'errorCode': 'ERROR_IP_BLOCKED',
    'errorDescription': "Your IP is blocked due to API inproper use. Check the reason at https://anti-captcha.com/panel/tools/ipsearch",
}

ERROR_TASK_ABSENT = {
    'errorId': 22,
    'errorCode': 'ERROR_TASK_ABSENT',
    'errorDescription': "Task property is empty or not set in createTask method. Please refer to API v2 documentation.",
}

ERROR_TASK_NOT_SUPPORTED = {
    'errorId': 23,
    'errorCode': 'ERROR_TASK_NOT_SUPPORTED',
    'errorDescription': "Task type is not supported or inproperly printed. Please check \"type\" parameter in task object.",
}

ERROR_INCORRECT_SESSION_DATA = {
    'errorId': 24,
    'errorCode': 'ERROR_INCORRECT_SESSION_DATA',
    'errorDescription': "Some of the required values for successive user emulation are missing.",
}

ERROR_PROXY_CONNECT_REFUSED = {
    'errorId': 25,
    'errorCode': 'ERROR_PROXY_CONNECT_REFUSED',
    'errorDescription': "Could not connect to proxy related to the task, connection refused",
}

ERROR_PROXY_CONNECT_TIMEOUT = {
    'errorId': 26,
    'errorCode': 'ERROR_PROXY_CONNECT_TIMEOUT',
    'errorDescription': "Could not connect to proxy related to the task, connection timeout",
}

ERROR_PROXY_READ_TIMEOUT = {
    'errorId': 27,
    'errorCode': 'ERROR_PROXY_READ_TIMEOUT',
    'errorDescription': "Connection to proxy for task has timed out",
}

ERROR_PROXY_BANNED = {
    'errorId': 28,
    'errorCode': 'ERROR_PROXY_BANNED',
    'errorDescription': "Proxy IP is banned by target service",
}

ERROR_PROXY_TRANSPARENT = {
    'errorId': 29,
    'errorCode': 'ERROR_PROXY_TRANSPARENT',
    'errorDescription': "Task denied at proxy checking state. Proxy must be non-transparent to hide our server IP.",
}

ERROR_RECAPTCHA_TIMEOUT = {
    'errorId': 30,
    'errorCode': 'ERROR_RECAPTCHA_TIMEOUT',
    'errorDescription': "Recaptcha task timeout, probably due to slow proxy server or Google server",
}

ERROR_RECAPTCHA_INVALID_SITEKEY = {
    'errorId': 31,
    'errorCode': 'ERROR_RECAPTCHA_INVALID_SITEKEY',
    'errorDescription': "Recaptcha server reported that site key is invalid",
}

ERROR_RECAPTCHA_INVALID_DOMAIN = {
    'errorId': 32,
    'errorCode': 'ERROR_RECAPTCHA_INVALID_DOMAIN',
    'errorDescription': "Recaptcha server reported that domain for this site key is invalid",
}

ERROR_RECAPTCHA_OLD_BROWSER = {
    'errorId': 33,
    'errorCode': 'ERROR_RECAPTCHA_OLD_BROWSER',
    'errorDescription': "Recaptcha server reported that browser user-agent is not compatible with their javascript",
}

ERROR_TOKEN_EXPIRED = {
    'errorId': 34,
    'errorCode': 'ERROR_TOKEN_EXPIRED',
    'errorDescription': "Captcha provider server reported that additional variable token has been expired. Please try again with new token.",
}

ERROR_PROXY_HAS_NO_IMAGE_SUPPORT = {
    'errorId': 35,
    'errorCode': 'ERROR_PROXY_HAS_NO_IMAGE_SUPPORT',
    'errorDescription': "Proxy does not support transfer of image data from Google servers",
}

ERROR_PROXY_INCOMPATIBLE_HTTP_VERSION = {
    'errorId': 36,
    'errorCode': 'ERROR_PROXY_INCOMPATIBLE_HTTP_VERSION',
    'errorDescription': "Proxy does not support long GET requests with length about 2000 bytes and does not support SSL connections",
}

ERROR_FACTORY_SERVER_API_CONNECTION_FAILED = {
    'errorId': 37,
    'errorCode': 'ERROR_FACTORY_SERVER_API_CONNECTION_FAILED',
    'errorDescription': "Could not connect to Factory Server API within 5 seconds",
}

ERROR_FACTORY_SERVER_BAD_JSON = {
    'errorId': 38,
    'errorCode': 'ERROR_FACTORY_SERVER_BAD_JSON',
    'errorDescription': "Incorrect Factory Server JSON response, something is broken",
}

ERROR_FACTORY_SERVER_ERRORID_MISSING = {
    'errorId': 39,
    'errorCode': 'ERROR_FACTORY_SERVER_ERRORID_MISSING',
    'errorDescription': "Factory Server API did not send any errorId",
}

ERROR_FACTORY_SERVER_ERRORID_NOT_ZERO = {
    'errorId': 40,
    'errorCode': 'ERROR_FACTORY_SERVER_ERRORID_NOT_ZERO',
    'errorDescription': "Factory Server API reported errorId != 0, check this error",
}

ERROR_FACTORY_MISSING_PROPERTY = {
    'errorId': 41,
    'errorCode': 'ERROR_FACTORY_MISSING_PROPERTY',
    'errorDescription': "Some of the required property values are missing in Factory form specifications. Customer must send all required values.",
}

ERROR_FACTORY_PROPERTY_INCORRECT_FORMAT = {
    'errorId': 42,
    'errorCode': 'ERROR_FACTORY_PROPERTY_INCORRECT_FORMAT',
    'errorDescription': "Expected other type of property value in Factory form structure. Customer must send specified value type.",
}

ERROR_FACTORY_ACCESS_DENIED = {
    'errorId': 43,
    'errorCode': 'ERROR_FACTORY_ACCESS_DENIED',
    'errorDescription': "Factory control belong to another account, check your account key.",
}

ERROR_FACTORY_SERVER_OPERATION_FAILED = {
    'errorId': 44,
    'errorCode': 'ERROR_FACTORY_SERVER_OPERATION_FAILED',
    'errorDescription': "Factory Server general error code",
}

ERROR_FACTORY_PLATFORM_OPERATION_FAILED = {
    'errorId': 45,
    'errorCode': 'ERROR_FACTORY_PLATFORM_OPERATION_FAILED',
    'errorDescription': "Factory Platform general error code.",
}

ERROR_FACTORY_PROTOCOL_BROKEN = {
    'errorId': 46,
    'errorCode': 'ERROR_FACTORY_PROTOCOL_BROKEN',
    'errorDescription': "Factory task lifetime protocol broken during task workflow.",
}

ERROR_FACTORY_TASK_NOT_FOUND = {
    'errorId': 47,
    'errorCode': 'ERROR_FACTORY_TASK_NOT_FOUND',
    'errorDescription': "Task not found or not available for this operation",
}

ERROR_FACTORY_IS_SANDBOXED = {
    'errorId': 48,
    'errorCode': 'ERROR_FACTORY_IS_SANDBOXED',
    'errorDescription': "Factory is sandboxed, creating tasks is possible only by Factory owner. Switch it to production mode to make it available for other customers.",
}

ERROR_PROXY_NOT_AUTHORISED = {
    'errorId': 49,
    'errorCode': 'ERROR_PROXY_NOT_AUTHORISED',
    'errorDescription': "Proxy login and password are incorrect",
}

ERROR_FUNCAPTCHA_NOT_ALLOWED = {
    'errorId': 50,
    'errorCode': 'ERROR_FUNCAPTCHA_NOT_ALLOWED',
    'errorDescription': "Customer did not enable Funcaptcha Proxyless tasks in Customers Area - API Settings.\nAll customers must read terms, pass mini test and sign/accept the form before being able to use this feature.",
}

ERROR_INVISIBLE_RECAPTCHA = {
    'errorId': 51,
    'errorCode': 'ERROR_INVISIBLE_RECAPTCHA',
    'errorDescription': "Recaptcha was attempted to be solved as usual one, instead of invisible mode. Basically you don't need to do anything when this error occurs, just continue sending tasks with this domain. Our system will self-learn to solve recaptchas from this sitekey in invisible mode.",
}

ERROR_FAILED_LOADING_WIDGET = {
    'errorId': 52,
    'errorCode': 'ERROR_FAILED_LOADING_WIDGET',
    'errorDescription': "Could not load captcha provider widget in worker browser. Please try sending new task.",
}

ERROR_VISIBLE_RECAPTCHA = {
    'errorId': 53,
    'errorCode': 'ERROR_VISIBLE_RECAPTCHA',
    'errorDescription': "Visible (v2) recaptcha was attempted to solved as invisible (v2)",
}

ERROR_ALL_WORKERS_FILTERED = {
    'errorId': 54,
    'errorCode': 'ERROR_ALL_WORKERS_FILTERED',
    'errorDescription': "No workers left which were not filtered by reportIncorrectRecaptcha method.",
}

ERROR_ACCOUNT_SUSPENDED = {
    'errorId': 55,
    'errorCode': 'ERROR_ACCOUNT_SUSPENDED',
    'errorDescription': "System suspended your account for a reason. Contact support for details.",
}
