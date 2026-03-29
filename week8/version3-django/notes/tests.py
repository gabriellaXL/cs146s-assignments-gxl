from django.test import TestCase
from django.urls import reverse

from .models import Note


class NoteViewsTests(TestCase):
    def test_list_page_renders_empty_state(self) -> None:
        response = self.client.get(reverse("notes:list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No notes yet")

    def test_create_note_persists_record(self) -> None:
        response = self.client.post(
            reverse("notes:create"),
            {
                "title": "Ship week 8",
                "content": "Finish the Django version with stable CRUD flows.",
                "status": Note.Status.ACTIVE,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, "Ship week 8")

    def test_create_note_shows_validation_errors(self) -> None:
        response = self.client.post(
            reverse("notes:create"),
            {
                "title": "Hi",
                "content": "Too short",
                "status": Note.Status.ACTIVE,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Title must be at least 3 characters long.")
        self.assertContains(response, "Content must be at least 10 characters long.")
        self.assertEqual(Note.objects.count(), 0)

    def test_update_note_changes_fields(self) -> None:
        note = Note.objects.create(
            title="Initial title",
            content="Initial content that is long enough.",
            status=Note.Status.ACTIVE,
        )

        response = self.client.post(
            reverse("notes:update", kwargs={"pk": note.pk}),
            {
                "title": "Updated title",
                "content": "Updated content that is also long enough.",
                "status": Note.Status.BLOCKED,
            },
        )

        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, "Updated title")
        self.assertEqual(note.status, Note.Status.BLOCKED)

    def test_delete_note_removes_record(self) -> None:
        note = Note.objects.create(
            title="Cleanup",
            content="Delete stale note content from the backlog.",
            status=Note.Status.ARCHIVED,
        )

        response = self.client.post(reverse("notes:delete", kwargs={"pk": note.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=note.pk).exists())
