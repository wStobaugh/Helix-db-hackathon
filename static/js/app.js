// static/js/app.js

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || `Request failed with ${res.status}`);
  }
  return data;
}

// Helix form
const helixForm = document.getElementById("helix-form");
const helixResult = document.getElementById("helix-result");

helixForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  helixResult.textContent = "Loading...";
  const name = document.getElementById("helix-name").value;
  const age = document.getElementById("helix-age").value;

  try {
    const data = await postJSON("/api/helix/users", { name, age });
    helixResult.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    helixResult.textContent = `Error: ${err.message}`;
  }
});

// Selenium form
const seleniumForm = document.getElementById("selenium-form");
const seleniumResult = document.getElementById("selenium-result");

seleniumForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  seleniumResult.textContent = "Loading...";
  const url = document.getElementById("selenium-url").value;

  try {
    const data = await postJSON("/api/selenium/title", { url });
    seleniumResult.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    seleniumResult.textContent = `Error: ${err.message}`;
  }
});

// Agent form
const agentForm = document.getElementById("agent-form");
const agentResult = document.getElementById("agent-result");

agentForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  agentResult.textContent = "Loading...";
  const message = document.getElementById("agent-message").value;

  try {
    const data = await postJSON("/api/agent", { message });
    agentResult.textContent = data.answer || JSON.stringify(data, null, 2);
  } catch (err) {
    agentResult.textContent = `Error: ${err.message}`;
  }
});
