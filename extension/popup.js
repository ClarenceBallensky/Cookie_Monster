async function init() {
  const domainEl = document.getElementById("domain");
  const fpRowsEl = document.getElementById("first-party-rows");
  const tpRowsEl = document.getElementById("third-party-rows");

  const response = await browser.runtime.sendMessage({ type: "GET_COOKIES_FOR_ACTIVE_TAB" });

  domainEl.textContent = response.domain ?? "No site detected";

  fpRowsEl.innerHTML = "";
  response.firstParty.forEach(cookie => {
    const row = document.createElement("tr");
    row.innerHTML= `<td>${cookie.name}</td><td>${cookie.cookie_domain}</td>`;
    fpRowsEl.appendChild(row);
  });
  if (response.firstParty.length === 0){
    fpRowsEl.innerHTML = `<tr><td colspan="2">No first-party cookies</td></tr>`;
  }

  tpRowsEl.innerHTML = "";
  response.thirdParty.forEach(cookie => {
    const row = document.createElement("tr");
    row.innerHTML= `<td>${cookie.name}</td><td>${cookie.cookie_domain}</td>`;
    tpRowsEl.appendChild(row);
  });
  if (response.firstParty.length === 0){
    tpRowsEl.innerHTML = `<tr><td colspan="2">No first-party cookies</td></tr>`;
  }

  /*
  rowsEl.innerHTML = "";
  for (const cookie of response.cookies) {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${cookie.name}</td><td>${cookie.cookie_domain}</td>`;
    rowsEl.appendChild(row);
  }

  if (response.cookies.length === 0) {
    rowsEl.innerHTML = `<tr><td colspan="2">No cookies observed yet.</td></tr>`;
  }
    */
}

document.addEventListener("DOMContentLoaded", init);