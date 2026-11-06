// Listens for requests from the popup and returns the cookies observed
// for the currently active tab's site.

browser.runtime.onMessage.addListener((message) => {
  if (message?.type === "GET_COOKIES_FOR_ACTIVE_TAB") {
    return getCookiesForActiveTab();
  }
});

/*
browser.webRequest.onHeadersReceived.addListener((details) => {
  console.log("web request url: " + details.url);
},
{urls: ["<all_urls>"]},
["responseHeaders"]
);
*/

browser.cookies.onChanged.addListener((info) => {
  if (info.removed) return;

  const cookie = info.cookie;

  // active tab check
  const tabs = browser.tabs.query({active: true, currentWindow: true});
  const activeTab = tabs[0];

  // return if not on correct tab
  if (!activeTab || !activeTab.url) return;

  console.log("Cookie name: ", cookie.name);
});

async function getCookiesForActiveTab() {
  const [activeTab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!activeTab?.url) {
    return { domain: null, cookies: [] };
  }

  const url = new URL(activeTab.url);
  const domain = url.hostname;

  // getAll({ url }) captures cookies visible to that URL — this covers
  // first-party cookies. Third-party cookies set by other domains during
  // the page load need a broader scan or webRequest — left as a TODO
  // for the full capture implementation (see docs/DATA_CONTRACTS.md, Contract 3).
  const cookies = await browser.cookies.getAll({ url: activeTab.url });

  return {
    domain,
    cookies: cookies.map((c) => ({
      name: c.name,
      cookie_domain: c.domain
    }))
  };
}

async function getCookiesWebRequest() {
  
}