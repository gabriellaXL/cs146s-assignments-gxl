async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

const actionFilters = {
  completed: false,
  project_id: '',
};

async function loadNotes(params = {}) {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const notes = await fetchJSON('/notes/?' + query.toString());
  for (const n of notes) {
    const li = document.createElement('li');
    li.textContent = `${n.title}: ${n.content}`;
    list.appendChild(li);
  }
}

async function loadActions(params = {}) {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const query = new URLSearchParams(params);
  const items = await fetchJSON('/action-items/?' + query.toString());
  for (const a of items) {
    const li = document.createElement('li');
    const projectLabel = a.project ? ` @ ${a.project.name}` : '';
    li.textContent = `${a.description}${projectLabel} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions(params);
      };
      li.appendChild(btn);
    } else {
      const btn = document.createElement('button');
      btn.textContent = 'Reopen';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ completed: false }),
        });
        loadActions(params);
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

function actionQueryParams() {
  const params = {};
  if (actionFilters.completed) {
    params.completed = true;
  }
  if (actionFilters.project_id) {
    params.project_id = actionFilters.project_id;
  }
  return params;
}

async function loadProjects() {
  const projectList = document.getElementById("projects");
  const createSelect = document.getElementById("action-project");
  const filterSelect = document.getElementById("action-project-filter");

  projectList.innerHTML = "";
  createSelect.innerHTML = '<option value="">No project</option>';
  filterSelect.innerHTML = '<option value="">All projects</option>';

  const projects = await fetchJSON("/projects/");
  for (const project of projects) {
    const li = document.createElement("li");
    li.textContent = `${project.name} (${project.action_item_count} tasks)`;
    if (project.description) {
      li.textContent += `: ${project.description}`;
    }
    projectList.appendChild(li);

    const createOption = document.createElement("option");
    createOption.value = project.id;
    createOption.textContent = project.name;
    createSelect.appendChild(createOption);

    const filterOption = document.createElement("option");
    filterOption.value = project.id;
    filterOption.textContent = project.name;
    filterSelect.appendChild(filterOption);
  }
}

window.addEventListener('DOMContentLoaded', () => {
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

  document.getElementById('note-search-btn').addEventListener('click', async () => {
    const q = document.getElementById('note-search').value;
    loadNotes({ q });
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    const projectId = document.getElementById('action-project').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        description,
        project_id: projectId ? Number(projectId) : null,
      }),
    });
    e.target.reset();
    await loadProjects();
    loadActions(actionQueryParams());
  });

  document.getElementById('filter-completed').addEventListener('change', (e) => {
    actionFilters.completed = e.target.checked;
    loadActions(actionQueryParams());
  });

  document.getElementById('action-project-filter').addEventListener('change', (e) => {
    actionFilters.project_id = e.target.value;
    loadActions(actionQueryParams());
  });

  document.getElementById('project-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('project-name').value;
    const description = document.getElementById('project-description').value;
    await fetchJSON('/projects/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, description: description || null }),
    });
    e.target.reset();
    await loadProjects();
  });

  loadNotes();
  loadProjects();
  loadActions(actionQueryParams());
});

