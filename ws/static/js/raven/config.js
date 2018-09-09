// Ignore list based off: https://gist.github.com/1878283
Raven.config('https://8ca35907a538416cbfad696d187acdc0@sentry.io/104648', {
  logger: 'javascript',
  ignoreErrors: [
    // Random plugins/extensions
    'top.GLOBALS',
    // See: https://blog.errorception.com/2012/03/tale-of-unfindable-js-error. html
    'originalCreateNotification',
    'canvas.contentDocument',
    'http://tt.epicplay.com',
    'Can\'t find variable: ZiteReader',
    'jigsaw is not defined',
    'ComboSearch is not defined',
    'http://loading.retry.widdit.com/',
    'atomicFindClose',
    // ISP "optimizing" proxy - `Cache-Control: no-transform` seems to reduce this. (thanks @acdha)
    // See https://stackoverflow.com/questions/4113268/how-to-stop-javascript-injection-from-vodafone-proxy
    'bmi_SafeAddOnload',
    'EBCallBackMessageReceived',
    // See https://toolbar.conduit.com/Developer/HtmlAndGadget/Methods/JSInjection.aspx
    'conduitPage',
    // Known error with Chrome Mobile iOS
    '__gCrWeb.autofill.extractForms',
    '__gCrWeb.contextualSearch.handleTapAtPoint'
  ],
  ignoreUrls: [
    // Chrome extensions
    /extensions\//i,
    /^chrome:\/\//i,
    // Other plugins
    /127\.0\.0\.1:4001\/isrunning/i,  // Cacaoweb
    /webappstoolbarba\.texthelp\.com\//i,
    /metrics\.itunes\.apple\.com\.edgesuite\.net\//i
  ]
}).install();
