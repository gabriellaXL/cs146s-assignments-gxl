async function fetchJSON(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = "Request failed";
    try {
      const data = await response.json();
      detail = data.detail || JSON.stringify(data);
    } catch {
      detail = await response.text();
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

const state = {
  notes: [],
  selectedNoteId: null,
  editingNoteId: null,
  search: "",
  sort: "-updated_at",
};

function $(id) {
  return document.getElementById(id);
}

function showMessage(message, type = "success") {
  const el = $("message");
  el.textContent = message;
  el.className = `message ${type}`;
  el.classList.remove("hidden");
}

function clearMessage() {
  const el = $("message");
  el.textContent = "";
  el.className = "message hidden";
}

function resetForm() {
  $("note-form").reset();
  $("note-id").value = "";
  $("note-status").value = "active";
  state.editingNoteId = null;
  $("detail-heading").textContent = "Create note";
  $("detail-copy").textContent = "Add a new note or edit an existing one.";
  $("save-note-btn").textContent = "Save note";
  $("cancel-edit-btn").classList.add("hidden");
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderNotes() {
  const list = $("notes");
  const emptyState = $("empty-state");
  list.innerHTML = "";

  if (state.notes.length === 0) {
    emptyState.classList.remove("hidden");
    return;
  }

  emptyState.classList.add("hidden");

  for (const note of state.notes) {
    const item = document.createElement("li");
    item.className = "note-card";
    item.innerHTML = `
      <div class="note-card-header">
        <div>
          <h3>${escapeHtml(note.title)}</h3>
          <span class="status-badge">${escapeHtml(note.status)}</span>
        </div>
        <small>Updated ${new Date(note.updated_at).toLocaleString()}</small>
      </div>
      <p>${escapeHtml(note.content.slice(0, 180))}${note.content.length > 180 ? "..." : ""}</p>
      <div class="note-card-actions">
        <button type="button" data-action="view" data-note-id="${note.id}" class="button">View</button>
        <button type="button" data-action="edit" data-note-id="${note.id}" class="button">Edit</button>
        <button type="button" data-action="delete" data-note-id="${note.id}" class="button button-danger">Delete</button>
      </div>
    `;
    list.appendChild(item);
  }
}

function renderDetail(note) {
  const detail = $("note-detail");
  if (!note) {
    detail.classList.add("hidden");
    return;
  }

  $("detail-title").textContent = note.title;
  $("detail-content").textContent = note.content;
  $("detail-status").textContent = note.status;
  $("detail-updated").textContent = `Updated ${new Date(note.updated_at).toLocaleString()}`;
  detail.classList.remove("hidden");
}

async function loadNotes() {
  clearMessage();
  const params = new URLSearchParams();
  if (state.search) {
    params.set("q", state.search);
  }
  params.set("sort", state.sort);

  const notes = await fetchJSON(`/notes/?${params.toString()}`);
  state.notes = notes;
  renderNotes();

  if (state.selectedNoteId) {
    const selected = state.notes.find((note) => note.id === state.selectedNoteId);
    renderDetail(selected || null);
  }
}

async function viewNote(noteId) {
  const note = await fetchJSON(`/notes/${noteId}`);
  state.selectedNoteId = note.id;
  renderDetail(note);
}

async function populateFormForEdit(noteId) {
  const note = await fetchJSON(`/notes/${noteId}`);
  state.editingNoteId = note.id;
  $("note-id").value = String(note.id);
  $("note-title").value = note.title;
  $("note-content").value = note.content;
  $("note-status").value = note.status;
  $("detail-heading").textContent = "Edit note";
  $("detail-copy").textContent = "Update an existing note and save the changes.";
  $("save-note-btn").textContent = "Update note";
  $("cancel-edit-btn").classList.remove("hidden");
}

async function submitForm(event) {
  event.preventDefault();
  clearMessage();

  const payload = {
    title: $("note-title").value.trim(),
    content: $("note-content").value.trim(),
    status: $("note-status").value,
  };

  if (state.editingNoteId) {
    await fetchJSON(`/notes/${state.editingNoteId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showMessage("Note updated successfully.");
    state.selectedNoteId = state.editingNoteId;
  } else {
    const created = await fetchJSON("/notes/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    showMessage("Note created successfully.");
    state.selectedNoteId = created.id;
  }

  resetForm();
  await loadNotes();
  if (state.selectedNoteId) {
    await viewNote(state.selectedNoteId);
  }
}

async function deleteNote(noteId) {
  const confirmed = window.confirm("Delete this note? This action cannot be undone.");
  if (!confirmed) {
    return;
  }

  clearMessage();
  await fetchJSON(`/notes/${noteId}`, { method: "DELETE" });
  if (state.selectedNoteId === noteId) {
    state.selectedNoteId = null;
    renderDetail(null);
  }
  if (state.editingNoteId === noteId) {
    resetForm();
  }
  showMessage("Note deleted successfully.");
  await loadNotes();
}

window.addEventListener("DOMContentLoaded", () => {
  $("note-form").addEventListener("submit", async (event) => {
    try {
      await submitForm(event);
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  $("note-search-btn").addEventListener("click", async () => {
    try {
      state.search = $("note-search").value.trim();
      state.sort = $("note-sort").value;
      await loadNotes();
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  $("new-note-btn").addEventListener("click", () => {
    resetForm();
    renderDetail(null);
  });

  $("cancel-edit-btn").addEventListener("click", () => {
    resetForm();
  });

  $("edit-note-btn").addEventListener("click", async () => {
    if (!state.selectedNoteId) {
      return;
    }
    try {
      await populateFormForEdit(state.selectedNoteId);
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  $("delete-note-btn").addEventListener("click", async () => {
    if (!state.selectedNoteId) {
      return;
    }
    try {
      await deleteNote(state.selectedNoteId);
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  $("notes").addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) {
      return;
    }

    const noteId = Number(button.dataset.noteId);
    const action = button.dataset.action;

    try {
      if (action === "view") {
        await viewNote(noteId);
      } else if (action === "edit") {
        await populateFormForEdit(noteId);
      } else if (action === "delete") {
        await deleteNote(noteId);
      }
    } catch (error) {
      showMessage(error.message, "error");
    }
  });

  loadNotes().catch((error) => {
    showMessage(error.message, "error");
  });
});
