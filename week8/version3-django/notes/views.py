from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import NoteForm
from .models import Note


class NoteListView(ListView):
    model = Note
    context_object_name = "notes"
    template_name = "notes/note_list.html"


class NoteDetailView(DetailView):
    model = Note
    context_object_name = "note"
    template_name = "notes/note_detail.html"


class NoteCreateView(CreateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/note_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Note created successfully.")
        return super().form_valid(form)


class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "notes/note_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Note updated successfully.")
        return super().form_valid(form)


class NoteDeleteView(DeleteView):
    model = Note
    template_name = "notes/note_confirm_delete.html"
    success_url = reverse_lazy("notes:list")

    def form_valid(self, form):
        messages.success(self.request, "Note deleted successfully.")
        return super().form_valid(form)
