async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    let message = 'Request failed';
    try {
      const payload = await res.json();
      if (Array.isArray(payload.detail)) {
        message = payload.detail.join('; ');
      } else if (payload.detail) {
        message = payload.detail;
      }
    } catch {
      message = await res.text();
    }
    throw new Error(message);
  }
  return res.json();
}

function setFeedback(id, message, isError = false) {
  const el = document.getElementById(id);
  el.textContent = message;
  el.classList.toggle('error', isError);
}

function resetNoteForm() {
  document.getElementById('note-form').reset();
  document.getElementById('note-id').value = '';
  document.getElementById('note-submit').textContent = 'Add';
  document.getElementById('note-cancel').hidden = true;
}

async function loadNotes(q) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const url = q ? `/notes/search/?q=${encodeURIComponent(q)}` : '/notes/';
  const notes = await fetchJSON(url);
  for (const n of notes) {
    const li = document.createElement('li');
    const text = document.createElement('span');
    text.textContent = `${n.title}: ${n.content}`;
    li.appendChild(text);

    const editBtn = document.createElement('button');
    editBtn.textContent = 'Edit';
    editBtn.onclick = () => {
      document.getElementById('note-id').value = n.id;
      document.getElementById('note-title').value = n.title;
      document.getElementById('note-content').value = n.content;
      document.getElementById('note-submit').textContent = 'Save';
      document.getElementById('note-cancel').hidden = false;
      setFeedback('note-feedback', `Editing note #${n.id}`);
    };
    li.appendChild(editBtn);

    const deleteBtn = document.createElement('button');
    deleteBtn.textContent = 'Delete';
    deleteBtn.onclick = async () => {
      try {
        const res = await fetch(`/notes/${n.id}`, { method: 'DELETE' });
        if (!res.ok) {
          throw new Error(`Delete failed with status ${res.status}`);
        }
        setFeedback('note-feedback', `Deleted note #${n.id}`);
        await loadNotes(document.getElementById('search-input').value.trim() || undefined);
      } catch (err) {
        setFeedback('note-feedback', err.message, true);
      }
    };
    li.appendChild(deleteBtn);
    list.appendChild(li);
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        try {
          await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
          setFeedback('action-feedback', `Completed action item #${a.id}`);
          loadActions();
        } catch (err) {
          setFeedback('action-feedback', err.message, true);
        }
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('search-btn').addEventListener('click', () => {
    const q = document.getElementById('search-input').value.trim();
    loadNotes(q || undefined);
  });

  document.getElementById('search-clear').addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    loadNotes();
  });

  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    const noteId = document.getElementById('note-id').value;
    const url = noteId ? `/notes/${noteId}` : '/notes/';
    const method = noteId ? 'PUT' : 'POST';
    try {
      await fetchJSON(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content }),
      });
      setFeedback('note-feedback', noteId ? `Updated note #${noteId}` : 'Added note');
      resetNoteForm();
      loadNotes();
    } catch (err) {
      setFeedback('note-feedback', err.message, true);
    }
  });

  document.getElementById('note-cancel').addEventListener('click', () => {
    resetNoteForm();
    setFeedback('note-feedback', 'Edit cancelled');
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    try {
      await fetchJSON('/action-items/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description }),
      });
      e.target.reset();
      setFeedback('action-feedback', 'Added action item');
      loadActions();
    } catch (err) {
      setFeedback('action-feedback', err.message, true);
    }
  });

  loadNotes();
  loadActions();
});
