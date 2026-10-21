const workspace = document.querySelector('#workspace');

function showPanel(name) {
  workspace.classList.remove('hidden');
  if (name === 'auth') {
    workspace.innerHTML = `<h3>Training access</h3><form id="auth-form"><label>Username</label><input name="username" required placeholder="student"><label>Email (needed for registration)</label><input name="email" type="email" placeholder="student@example.test"><label>Password</label><input name="password" type="password" required placeholder="Password"><button class="button primary" type="submit">Register</button> <button class="button ghost" type="button" id="login">Log in</button></form><pre id="result">Ready for a local test.</pre>`;
    document.querySelector('#auth-form').addEventListener('submit', e => sendForm(e, '/register'));
    document.querySelector('#login').addEventListener('click', () => sendForm(new Event('submit', {cancelable:true}), '/login'));
  } else {
    workspace.innerHTML = `<h3>Upload test file</h3><form id="upload-form"><label>Select a non-sensitive test file</label><input name="file" type="file" required><button class="button primary">Upload file</button></form><pre id="result">No file selected.</pre>`;
    document.querySelector('#upload-form').addEventListener('submit', async e => { e.preventDefault(); const r = await fetch('/upload',{method:'POST',body:new FormData(e.target)}); showResult(await r.json()); });
  }
  workspace.scrollIntoView({behavior:'smooth', block:'center'});
}

async function sendForm(event, endpoint) {
  event.preventDefault();
  const form = document.querySelector('#auth-form');
  const data = Object.fromEntries(new FormData(form));
  if (endpoint === '/login') delete data.email;
  const response = await fetch(endpoint, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  showResult(await response.json());
}
function showResult(data) { document.querySelector('#result').textContent = JSON.stringify(data, null, 2); }

document.querySelectorAll('[data-panel]').forEach(button => button.addEventListener('click', () => showPanel(button.dataset.panel)));
document.querySelectorAll('[data-request]').forEach(button => button.addEventListener('click', async () => { workspace.classList.remove('hidden'); workspace.innerHTML='<h3>Endpoint response</h3><pre id="result">Loading…</pre>'; workspace.scrollIntoView({behavior:'smooth',block:'center'}); const r=await fetch(button.dataset.request); showResult(await r.json()); }));

async function loadDashboard() {
  try {
    const data = await fetch('/api/dashboard').then(response => response.json());
    document.querySelector('#dashboard-mode').textContent = `Mode: ${data.mode}`;
    document.querySelector('#pipeline-status').textContent = data.pipeline.status;
    document.querySelector('#build-count').textContent = data.pipeline.builds;
    document.querySelector('#failed-count').textContent = data.pipeline.failed;
    document.querySelector('#critical-count').textContent = data.security.critical;
    document.querySelector('#high-count').textContent = data.security.high;
    document.querySelector('#medium-count').textContent = data.security.medium;
    document.querySelector('#low-count').textContent = data.security.low;
    document.querySelector('#runtime-response').textContent = data.runtime.response;
    document.querySelector('#alert-count').textContent = data.runtime.alerts;
    document.querySelector('#blocked-count').textContent = data.runtime.blocked;
    document.querySelector('#dashboard-updated').textContent = `Updated ${data.updated_at}`;
    document.querySelector('#event-list').innerHTML = data.events.map(event => `<div class="event-row"><span class="event-time">${event.time}</span><span class="risk-pill risk-${event.risk.toLowerCase()}">${event.risk}</span><span><b>${event.title}</b><span class="event-detail">${event.detail}</span></span><span class="event-action">${event.action}</span></div>`).join('');
  } catch { document.querySelector('#dashboard-mode').textContent = 'Dashboard data is unavailable.'; }
}
loadDashboard();
