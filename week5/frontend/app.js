// =============================================================================
// Utilities
// =============================================================================

/**
 * Fetch a JSON resource, handling 204 No Content and surfacing server-side
 * validation messages in a human-readable form.
 *
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>}  Parsed JSON body, or null for 204 responses.
 */
async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (res.status === 204) return null;
  const raw = await res.text();
  if (!res.ok) {
    let message = raw;
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed?.detail)) {
        message = parsed.detail.map((e) => e.msg).join('; ');
      } else {
        message = parsed?.detail ?? raw;
      }
    } catch (_) { /* not JSON */ }
    throw new Error(message);
  }
  return JSON.parse(raw);
}

/**
 * Show a transient error banner that auto-dismisses after 5 s.
 * @param {string} message
 */
function showError(message) {
  let banner = document.getElementById('error-banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'error-banner';
    banner.setAttribute('role', 'alert');
    banner.setAttribute('aria-live', 'assertive');
    document.querySelector('main').prepend(banner);
  }
  banner.textContent = message;
  banner.classList.add('visible');
  clearTimeout(banner._dismissTimer);
  banner._dismissTimer = setTimeout(() => banner.classList.remove('visible'), 5000);
}


// =============================================================================
// Notes — state & rendering
// =============================================================================

/** Single source of truth for the rendered notes list. */
let notes = [];

/** Re-render the notes list from current state. */
function renderNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  for (const note of notes) list.appendChild(buildNoteItem(note));
}

/** Build a display-mode <li> for a single note. */
function buildNoteItem(note) {
  const li = document.createElement('li');
  li.className = 'note-item';
  li.dataset.id = String(note.id);

  const text = document.createElement('span');
  text.className = 'note-text';
  text.textContent = `${note.title}: ${note.content}`;
  li.appendChild(text);

  const acts = document.createElement('span');
  acts.className = 'note-actions';

  const editBtn = document.createElement('button');
  editBtn.textContent = 'Edit';
  editBtn.className = 'btn-secondary';
  editBtn.addEventListener('click', () => enterEditMode(li, note));
  acts.appendChild(editBtn);

  const delBtn = document.createElement('button');
  delBtn.textContent = 'Delete';
  delBtn.className = 'btn-danger';
  delBtn.addEventListener('click', () => deleteNote(note.id));
  acts.appendChild(delBtn);

  li.appendChild(acts);
  return li;
}

/** Replace a note <li> with an inline edit form. */
function enterEditMode(li, note) {
  li.innerHTML = '';
  li.className = 'note-item note-item--editing';

  const titleInput = document.createElement('input');
  titleInput.className = 'edit-input';
  titleInput.value = note.title;
  titleInput.placeholder = 'Title';
  titleInput.required = true;
  titleInput.maxLength = 200;

  const contentInput = document.createElement('input');
  contentInput.className = 'edit-input';
  contentInput.value = note.content;
  contentInput.placeholder = 'Content';
  contentInput.required = true;

  const saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save';
  saveBtn.className = 'btn-primary';
  saveBtn.addEventListener('click', () => {
    const t = titleInput.value.trim();
    const c = contentInput.value.trim();
    if (!t || !c) { showError('Title and content cannot be empty.'); return; }
    updateNote(note.id, t, c);
  });

  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.className = 'btn-secondary';
  cancelBtn.addEventListener('click', renderNotes);

  li.append(titleInput, contentInput, saveBtn, cancelBtn);
  titleInput.focus();
  titleInput.select();
}


// =============================================================================
// Notes — CRUD (optimistic UI)
// =============================================================================

async function loadNotes() {
  try {
    notes = await fetchJSON('/notes/');
    renderNotes();
  } catch (err) {
    showError('Failed to load notes: ' + err.message);
  }
}

async function createNote(title, content) {
  const tempId = `temp-${Date.now()}`;
  notes = [...notes, { id: tempId, title, content }];
  renderNotes();
  try {
    const created = await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    notes = notes.map((n) => (n.id === tempId ? created : n));
    renderNotes();
  } catch (err) {
    notes = notes.filter((n) => n.id !== tempId);
    renderNotes();
    showError('Failed to create note: ' + err.message);
  }
}

async function updateNote(id, title, content) {
  const snapshot = notes.map((n) => ({ ...n }));
  notes = notes.map((n) => (n.id === id ? { ...n, title, content } : n));
  renderNotes();
  try {
    const updated = await fetchJSON(`/notes/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    notes = notes.map((n) => (n.id === id ? updated : n));
    renderNotes();
  } catch (err) {
    notes = snapshot;
    renderNotes();
    showError('Failed to update note: ' + err.message);
  }
}

async function deleteNote(id) {
  const snapshot = notes.map((n) => ({ ...n }));
  notes = notes.filter((n) => n.id !== id);
  renderNotes();
  try {
    await fetchJSON(`/notes/${id}`, { method: 'DELETE' });
  } catch (err) {
    notes = snapshot;
    renderNotes();
    showError('Failed to delete note: ' + err.message);
  }
}


// =============================================================================
// Action items — state (filter + bulk selection)
// =============================================================================

/** Current filter: 'all' | 'true' | 'false' */
let actionFilter = 'all';

/** IDs currently checked for bulk operations. */
const selectedIds = new Set();

/** Sync the selected-count label and bulk button state. */
function syncBulkUI() {
  const count = selectedIds.size;
  document.getElementById('selected-count').textContent =
    count === 1 ? '1 selected' : `${count} selected`;
  document.getElementById('bulk-complete-btn').disabled = count === 0;
}


// =============================================================================
// Action items — rendering
// =============================================================================

async function loadActions() {
  try {
    const list = document.getElementById('actions');
    list.innerHTML = '';

    const url = new URL('/action-items/', location.origin);
    if (actionFilter !== 'all') url.searchParams.set('completed', actionFilter);

    const items = await fetchJSON(url.toString());

    // Prune selectedIds for items no longer visible after filter change
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

      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = selectedIds.has(a.id);
      cb.setAttribute('aria-label', `Select "${a.description}"`);
      cb.addEventListener('change', () => {
        if (cb.checked) selectedIds.add(a.id); else selectedIds.delete(a.id);
        syncBulkUI();
      });

      const badge = document.createElement('span');
      badge.className = a.completed ? 'badge badge-done' : 'badge badge-open';
      badge.textContent = a.completed ? 'done' : 'open';

      const label = document.createElement('span');
      label.className = 'action-desc';
      label.textContent = a.description;

      li.appendChild(cb);
      li.appendChild(badge);
      li.appendChild(label);

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
            btn.disabled = false;
            showError('Failed to complete item: ' + err.message);
          }
        });
        li.appendChild(btn);
      }

      list.appendChild(li);
    }
  } catch (err) {
    showError('Failed to load action items: ' + err.message);
  }
}


// =============================================================================
// Action items — bulk complete
// =============================================================================

async function bulkComplete() {
  if (selectedIds.size === 0) return;

  const btn = document.getElementById('bulk-complete-btn');
  btn.disabled = true;
  btn.textContent = 'Working\u2026';

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
    showError('Bulk complete failed: ' + err.message);
  } finally {
    btn.textContent = 'Mark Selected Done';
    syncBulkUI();
  }
}


// =============================================================================
// Initialization
// =============================================================================

window.addEventListener('DOMContentLoaded', () => {
  // Notes form — create with optimistic UI
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    if (!title || !content) { showError('Title and content cannot be empty.'); return; }
    await createNote(title, content);
    e.target.reset();
  });

  // Action items form — create
  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value.trim();
    if (!description) { showError('Description cannot be empty.'); return; }
    try {
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      e.target.reset();
      loadActions();
    } catch (err) {
      showError('Failed to create action item: ' + err.message);
    }
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

  loadNotes();
  loadActions();
});