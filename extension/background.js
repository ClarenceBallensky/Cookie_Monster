// Listens for requests from the popup and returns the cookies observed
// for the currently active tab's site.

//const { act } = require("react");

browser.runtime.onMessage.addListener((message) => {
  if (message?.type === "GET_COOKIES_FOR_ACTIVE_TAB") {
    return getCookiesForActiveTab();
  }
});

// keep a list of third party cookies gathered by this session
const capturedCookies = [];


/*
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
  */

async function getCookiesForActiveTab() {
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true});
  if (!tab?.url || tab.url.startsWith("about:")) return {domain: null, cookies: []};

  const domain = new URL(tab.url).hostname;
  const cookies = await browser.cookies.getAll({});

  const firstParty = [];
  const thirdParty = [];

  cookies.forEach(c => {
    const clean = c.domain.replace(/^\./, '');
    const isFirst = domain === clean || domain.endsWith('.' + clean);
    const item = {name: c.name, cookie_domain: c.domain};

    if (isFirst){
      firstParty.push(item);
    } else{
      thirdParty.push(item);
    }
  });

  return {domain, firstParty, thirdParty}
}