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
        // FastAPI validation error — join individual field messages
        message = parsed.detail.map((e) => e.msg).join('; ');
      } else {
        message = parsed?.detail ?? raw;
      }
    } catch (_) { /* not JSON — use raw text */ }
    throw new Error(message);
  }

  return JSON.parse(raw);
}

/**
 * Show a transient error banner that auto-dismisses after 5 s.
 * Creates the banner element on first call if it does not yet exist.
 *
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

/**
 * Re-render the full notes list from the current `notes` array.
 * Replaces the DOM contents of #notes.
 */
function renderNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  for (const note of notes) {
    list.appendChild(buildNoteItem(note));
  }
}

/**
 * Build a <li> element representing a single note in display mode.
 *
 * @param {{ id: number|string, title: string, content: string }} note
 * @returns {HTMLLIElement}
 */
function buildNoteItem(note) {
  const li = document.createElement('li');
  li.className = 'note-item';
  li.dataset.id = String(note.id);

  const text = document.createElement('span');
  text.className = 'note-text';
  text.textContent = `${note.title}: ${note.content}`;
  li.appendChild(text);

  const actions = document.createElement('span');
  actions.className = 'note-actions';

  const editBtn = document.createElement('button');
  editBtn.textContent = 'Edit';
  editBtn.className = 'btn-secondary';
  editBtn.addEventListener('click', () => enterEditMode(li, note));
  actions.appendChild(editBtn);

  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = 'Delete';
  deleteBtn.className = 'btn-danger';
  deleteBtn.addEventListener('click', () => deleteNote(note.id));
  actions.appendChild(deleteBtn);

  li.appendChild(actions);
  return li;
}

/**
 * Replace the content of `li` with an inline edit form.
 * Submitting the form triggers an optimistic PUT request.
 *
 * @param {HTMLLIElement} li
 * @param {{ id: number, title: string, content: string }} note
 */
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
    const newTitle = titleInput.value.trim();
    const newContent = contentInput.value.trim();
    if (!newTitle || !newContent) {
      showError('Title and content cannot be empty.');
      return;
    }
    updateNote(note.id, newTitle, newContent);
  });

  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.className = 'btn-secondary';
  cancelBtn.addEventListener('click', renderNotes); // restore display mode

  li.append(titleInput, contentInput, saveBtn, cancelBtn);
  titleInput.focus();
  titleInput.select();
}


// =============================================================================
// Notes — CRUD actions (with optimistic UI)
// =============================================================================

/** Fetch notes from the server and refresh the rendered list. */
async function loadNotes() {
  try {
    notes = await fetchJSON('/notes/');
    renderNotes();
  } catch (err) {
    showError('Failed to load notes: ' + err.message);
  }
}

/**
 * Optimistically add a note to the list, POST to the server, then reconcile
 * with the server-assigned id. Rolls back on error.
 *
 * @param {string} title
 * @param {string} content
 */
async function createNote(title, content) {
  const tempId = `temp-${Date.now()}`;
  const optimistic = { id: tempId, title, content };
  notes = [...notes, optimistic];
  renderNotes();

  try {
    const created = await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    // Replace the temp placeholder with the authoritative server record
    notes = notes.map((n) => (n.id === tempId ? created : n));
    renderNotes();
  } catch (err) {
    // Rollback
    notes = notes.filter((n) => n.id !== tempId);
    renderNotes();
    showError('Failed to create note: ' + err.message);
  }
}

/**
 * Optimistically apply the edit in the UI, PUT to the server, then sync with
 * the server response. Rolls back on error.
 *
 * @param {number} id
 * @param {string} title
 * @param {string} content
 */
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
    // Sync with the server's canonical response (e.g. server-side trimming)
    notes = notes.map((n) => (n.id === id ? updated : n));
    renderNotes();
  } catch (err) {
    notes = snapshot; // rollback to pre-edit state
    renderNotes();
    showError('Failed to update note: ' + err.message);
  }
}

/**
 * Optimistically remove the note from the list, then DELETE on the server.
 * Rolls back on error.
 *
 * @param {number} id
 */
async function deleteNote(id) {
  const snapshot = notes.map((n) => ({ ...n }));
  notes = notes.filter((n) => n.id !== id);
  renderNotes();

  try {
    await fetchJSON(`/notes/${id}`, { method: 'DELETE' });
  } catch (err) {
    notes = snapshot; // rollback
    renderNotes();
    showError('Failed to delete note: ' + err.message);
  }
}


// =============================================================================
// Action items
// =============================================================================

/** Fetch action items from the server and refresh the rendered list. */
async function loadActions() {
  try {
    const list = document.getElementById('actions');
    list.innerHTML = '';
    const items = await fetchJSON('/action-items/');
    for (const a of items) {
      list.appendChild(buildActionItem(a));
    }
  } catch (err) {
    showError('Failed to load action items: ' + err.message);
  }
}

/**
 * Build a <li> element for a single action item.
 *
 * @param {{ id: number, description: string, completed: boolean }} a
 * @returns {HTMLLIElement}
 */
function buildActionItem(a) {
  const li = document.createElement('li');
  li.className = 'action-item' + (a.completed ? ' action-item--done' : '');
  li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;

  if (!a.completed) {
    const btn = document.createElement('button');
    btn.textContent = 'Complete';
    btn.className = 'btn-secondary';
    btn.addEventListener('click', async () => {
      btn.disabled = true;
      try {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      } catch (err) {
        btn.disabled = false;
        showError('Failed to complete action: ' + err.message);
      }
    });
    li.appendChild(btn);
  }

  return li;
}


// =============================================================================
// Initialization
// =============================================================================

window.addEventListener('DOMContentLoaded', () => {
  // Note form — create
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value.trim();
    const content = document.getElementById('note-content').value.trim();
    if (!title || !content) {
      showError('Title and content cannot be empty.');
      return;
    }
    await createNote(title, content);
    e.target.reset();
  });

  // Action item form — create
  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value.trim();
    if (!description) {
      showError('Description cannot be empty.');
      return;
    }
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

  loadNotes();
  loadActions();
});
