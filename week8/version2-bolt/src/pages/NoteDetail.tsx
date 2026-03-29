import { useEffect, useState } from 'react';
import { ArrowLeft, CreditCard as Edit, Trash2 } from 'lucide-react';
import { parseRoute } from '../lib/route-utils';
import { useRouter } from '../lib/router-context';
import { getNoteById, deleteNote } from '../services/notes';
import type { Note } from '../lib/database.types';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { DeleteConfirmation } from '../components/DeleteConfirmation';

const STATUS_STYLES = {
  active: 'bg-green-100 text-green-800',
  blocked: 'bg-red-100 text-red-800',
  archived: 'bg-gray-100 text-gray-800',
} as const;

export function NoteDetail() {
  const { currentPath, navigate } = useRouter();
  const [note, setNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const params = parseRoute('/notes/:id', currentPath);
  const noteId = params?.id;

  useEffect(() => {
    if (noteId) {
      loadNote(noteId);
    }
  }, [noteId]);

  async function loadNote(id: string) {
    setLoading(true);
    setError(null);
    const result = await getNoteById(id);

    if (result.error) {
      setError(result.error);
    } else if (result.data) {
      setNote(result.data);
    }

    setLoading(false);
  }

  async function handleDelete() {
    if (!noteId) return;

    setDeleting(true);
    const result = await deleteNote(noteId);

    if (result.error) {
      setError(result.error);
      setDeleting(false);
    } else {
      navigate('/');
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading note...</div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="max-w-4xl mx-auto">
        <Button
          variant="secondary"
          onClick={() => navigate('/')}
          className="mb-6 flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Notes
        </Button>
        <Alert type="error" message={error || 'Note not found'} />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="secondary"
          onClick={() => navigate('/')}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Notes
        </Button>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => navigate(`/notes/${note.id}/edit`)}
            className="flex items-center gap-2"
          >
            <Edit className="w-4 h-4" />
            Edit
          </Button>
          <Button
            variant="danger"
            onClick={() => setDeleteModalOpen(true)}
            className="flex items-center gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </Button>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-8">
        <div className="flex items-start justify-between gap-4 mb-6">
          <h1 className="text-3xl font-bold text-gray-900">{note.title}</h1>
          <span className={`px-3 py-1 text-sm font-medium rounded ${STATUS_STYLES[note.status]}`}>
            {note.status}
          </span>
        </div>

        <div className="prose max-w-none mb-8">
          <p className="text-gray-700 whitespace-pre-wrap">{note.content}</p>
        </div>

        <div className="border-t border-gray-200 pt-6">
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="font-medium text-gray-500">Created</dt>
              <dd className="mt-1 text-gray-900">
                {new Date(note.created_at).toLocaleString()}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Last Updated</dt>
              <dd className="mt-1 text-gray-900">
                {new Date(note.updated_at).toLocaleString()}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      <DeleteConfirmation
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        onConfirm={handleDelete}
        title={note.title}
        isDeleting={deleting}
      />
    </div>
  );
}
