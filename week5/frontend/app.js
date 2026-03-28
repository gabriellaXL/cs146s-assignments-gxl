// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------

async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ---------------------------------------------------------------------------
// Notes
// ---------------------------------------------------------------------------

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

// ---------------------------------------------------------------------------
// Action Items — state
// ---------------------------------------------------------------------------

/** Current filter: 'all' | 'true' | 'false' */
let actionFilter = 'all';

/** IDs of items currently checked by the user. */
const selectedIds = new Set();

/** Re-render the selected-count label and toggle the bulk button. */
function syncBulkUI() {
  const count = selectedIds.size;
  document.getElementById('selected-count').textContent =
    count === 1 ? '1 selected' : `${count} selected`;
  document.getElementById('bulk-complete-btn').disabled = count === 0;
}

// ---------------------------------------------------------------------------
// Action Items — rendering
// ---------------------------------------------------------------------------

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';

  // Build URL with optional filter param
  const url = new URL('/action-items/', location.origin);
  if (actionFilter !== 'all') {
    url.searchParams.set('completed', actionFilter);
  }

  const items = await fetchJSON(url.toString());

  // Remove IDs from selectedIds that are no longer visible
  const visibleIds = new Set(items.map((a) => a.id));
  for (const id of [...selectedIds]) {
    if (!visibleIds.has(id)) selectedIds.delete(id);
  }
  syncBulkUI();

  if (items.length === 0) {
    const li = document.createElement('li');
    li.className = 'empty-msg';
    li.textContent = 'No items to show.';
    list.appendChild(li);
    return;
  }

  for (const a of items) {
    const li = document.createElement('li');
    li.className = 'action-item';

    // Checkbox for bulk selection
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.checked = selectedIds.has(a.id);
    cb.setAttribute('aria-label', `Select "${a.description}"`);
    cb.addEventListener('change', () => {
      if (cb.checked) {
        selectedIds.add(a.id);
      } else {
        selectedIds.delete(a.id);
      }
      syncBulkUI();
    });

    // Status badge
    const badge = document.createElement('span');
    badge.className = a.completed ? 'badge badge-done' : 'badge badge-open';
    badge.textContent = a.completed ? 'done' : 'open';

    // Description text
    const label = document.createElement('span');
    label.className = 'action-desc';
    label.textContent = a.description;

    li.appendChild(cb);
    li.appendChild(badge);
    li.appendChild(label);

    // Per-item complete button (only for open items)
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.addEventListener('click', async () => {
        btn.disabled = true;
        try {
          await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
          selectedIds.delete(a.id);
          await loadActions();
        } catch (err) {
          console.error('Failed to complete item:', err);
          btn.disabled = false;
        }
      });
      li.appendChild(btn);
    }

    list.appendChild(li);
  }
}

// ---------------------------------------------------------------------------
// Action Items — bulk complete
// ---------------------------------------------------------------------------

async function bulkComplete() {
  if (selectedIds.size === 0) return;

  const btn = document.getElementById('bulk-complete-btn');
  btn.disabled = true;
  btn.textContent = 'Working…';

  try {
    const result = await fetchJSON('/action-items/bulk-complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ids: [...selectedIds] }),
    });
    console.info(`Bulk-completed ${result.updated} item(s).`);
    selectedIds.clear();
    await loadActions();
  } catch (err) {
    console.error('Bulk complete failed:', err);
    alert(`Bulk complete failed: ${err.message}`);
  } finally {
    btn.textContent = 'Mark Selected Done';
    syncBulkUI(); // re-enables/disables based on remaining selection
  }
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

window.addEventListener('DOMContentLoaded', () => {
  // Notes form
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  // Action items form
  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  // Filter buttons
  document.querySelectorAll('.filter-bar button').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-bar button').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      actionFilter = btn.dataset.filter;
      selectedIds.clear();
      loadActions();
    });
  });

  // Bulk complete button
  document.getElementById('bulk-complete-btn').addEventListener('click', bulkComplete);

  // Initial load
  loadNotes();
  loadActions();
});
