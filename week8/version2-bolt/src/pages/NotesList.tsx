import { useEffect, useState } from 'react';
import { FileText, ChevronRight } from 'lucide-react';
import { getNotes } from '../services/notes';
import type { Note } from '../lib/database.types';
import { Alert } from '../components/ui/Alert';
import { useRouter } from '../lib/router-context';

const STATUS_STYLES = {
  active: 'bg-green-100 text-green-800',
  blocked: 'bg-red-100 text-red-800',
  archived: 'bg-gray-100 text-gray-800',
} as const;

export function NotesList() {
  const { navigate } = useRouter();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadNotes();
  }, []);

  async function loadNotes() {
    setLoading(true);
    setError(null);
    const result = await getNotes();

    if (result.error) {
      setError(result.error);
    } else {
      setNotes(result.data || []);
    }

    setLoading(false);
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading notes...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Alert type="error" message={error} />
      </div>
    );
  }

  if (notes.length === 0) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg border border-gray-200 p-12 text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">No notes yet</h2>
          <p className="text-gray-600 mb-6">
            Get started by creating your first note
          </p>
          <button
            onClick={() => navigate('/notes/new')}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create your first note
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-semibold text-gray-900">All Notes</h2>
        <p className="text-gray-600 mt-1">{notes.length} {notes.length === 1 ? 'note' : 'notes'}</p>
      </div>

      <div className="space-y-3">
        {notes.map((note) => (
          <button
            key={note.id}
            onClick={() => navigate(`/notes/${note.id}`)}
            className="w-full bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all text-left group"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 truncate group-hover:text-blue-600">
                    {note.title}
                  </h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded ${STATUS_STYLES[note.status]}`}>
                    {note.status}
                  </span>
                </div>
                <p className="text-gray-600 line-clamp-2">{note.content}</p>
                <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                  <span>Created {new Date(note.created_at).toLocaleDateString()}</span>
                  <span>Updated {new Date(note.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 flex-shrink-0" />
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
