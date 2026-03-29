import { useEffect, useState } from 'react';
import { ArrowLeft } from 'lucide-react';
import { useRouter, parseRoute } from '../lib/router';
import { getNoteById, createNote, updateNote, ValidationError } from '../services/notes';
import type { NoteStatus } from '../lib/database.types';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { TextArea } from '../components/ui/TextArea';
import { Select } from '../components/ui/Select';
import { Alert } from '../components/ui/Alert';

const STATUS_OPTIONS = [
  { value: 'active', label: 'Active' },
  { value: 'blocked', label: 'Blocked' },
  { value: 'archived', label: 'Archived' },
];

export function NoteForm() {
  const { currentPath, navigate } = useRouter();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [status, setStatus] = useState<NoteStatus>('active');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});

  const isEditMode = currentPath.includes('/edit');
  const params = parseRoute('/notes/:id/edit', currentPath);
  const noteId = params?.id;

  useEffect(() => {
    if (isEditMode && noteId) {
      loadNote(noteId);
    } else {
      setInitialLoading(false);
    }
  }, [isEditMode, noteId]);

  async function loadNote(id: string) {
    setInitialLoading(true);
    const result = await getNoteById(id);

    if (result.error) {
      setError(result.error);
    } else if (result.data) {
      setTitle(result.data.title);
      setContent(result.data.content);
      setStatus(result.data.status);
    }

    setInitialLoading(false);
  }

  function clearMessages() {
    setError(null);
    setSuccess(null);
    setValidationErrors({});
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    clearMessages();
    setLoading(true);

    const noteData = {
      title: title.trim(),
      content: content.trim(),
      status,
    };

    let result;
    if (isEditMode && noteId) {
      result = await updateNote(noteId, noteData);
    } else {
      result = await createNote(noteData);
    }

    if (result.validationErrors) {
      const errors: Record<string, string> = {};
      result.validationErrors.forEach((err: ValidationError) => {
        errors[err.field] = err.message;
      });
      setValidationErrors(errors);
      setLoading(false);
    } else if (result.error) {
      setError(result.error);
      setLoading(false);
    } else if (result.data) {
      setSuccess(isEditMode ? 'Note updated successfully' : 'Note created successfully');
      setTimeout(() => {
        navigate(`/notes/${result.data!.id}`);
      }, 1000);
    }
  }

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading note...</div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <Button
        variant="secondary"
        onClick={() => navigate(isEditMode && noteId ? `/notes/${noteId}` : '/')}
        className="mb-6 flex items-center gap-2"
      >
        <ArrowLeft className="w-4 h-4" />
        {isEditMode ? 'Back to Note' : 'Back to Notes'}
      </Button>

      <div className="bg-white rounded-lg border border-gray-200 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          {isEditMode ? 'Edit Note' : 'Create New Note'}
        </h1>

        {error && (
          <div className="mb-6">
            <Alert type="error" message={error} />
          </div>
        )}

        {success && (
          <div className="mb-6">
            <Alert type="success" message={success} />
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Input
            label="Title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            error={validationErrors.title}
            placeholder="Enter note title (min 3 characters)"
            disabled={loading}
          />

          <TextArea
            label="Content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            error={validationErrors.content}
            placeholder="Enter note content (min 10 characters)"
            rows={10}
            disabled={loading}
          />

          <Select
            label="Status"
            value={status}
            onChange={(e) => setStatus(e.target.value as NoteStatus)}
            options={STATUS_OPTIONS}
            disabled={loading}
          />

          <div className="flex gap-3 pt-4">
            <Button type="submit" disabled={loading} className="flex-1">
              {loading ? 'Saving...' : isEditMode ? 'Update Note' : 'Create Note'}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate(isEditMode && noteId ? `/notes/${noteId}` : '/')}
              disabled={loading}
            >
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
