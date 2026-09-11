async function init() {
  const domainEl = document.getElementById("domain");
  const rowsEl = document.getElementById("cookie-rows");

  const response = await browser.runtime.sendMessage({ type: "GET_COOKIES_FOR_ACTIVE_TAB" });

  domainEl.textContent = response.domain ?? "No site detected";

  rowsEl.innerHTML = "";
  for (const cookie of response.cookies) {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${cookie.name}</td><td>${cookie.cookie_domain}</td>`;
    rowsEl.appendChild(row);
  }

  if (response.cookies.length === 0) {
    rowsEl.innerHTML = `<tr><td colspan="2">No cookies observed yet.</td></tr>`;
  }
}

document.addEventListener("DOMContentLoaded", init);