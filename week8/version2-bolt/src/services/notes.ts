import { supabase } from '../lib/supabase';
import type { Note, NoteInsert, NoteUpdate } from '../lib/database.types';

export interface ValidationError {
  field: string;
  message: string;
}

export interface ServiceResult<T> {
  data?: T;
  error?: string;
  validationErrors?: ValidationError[];
}

function asNoteArray(data: unknown): Note[] {
  return (data as Note[]) || [];
}

function asNote(data: unknown): Note {
  return data as Note;
}

export function validateNote(data: { title?: string; content?: string }): ValidationError[] {
  const errors: ValidationError[] = [];

  if (!data.title || data.title.trim().length === 0) {
    errors.push({ field: 'title', message: 'Title is required' });
  } else if (data.title.trim().length < 3) {
    errors.push({ field: 'title', message: 'Title must be at least 3 characters' });
  }

  if (!data.content || data.content.trim().length === 0) {
    errors.push({ field: 'content', message: 'Content is required' });
  } else if (data.content.trim().length < 10) {
    errors.push({ field: 'content', message: 'Content must be at least 10 characters' });
  }

  return errors;
}

export async function getNotes(): Promise<ServiceResult<Note[]>> {
  try {
    const { data, error } = await supabase
      .from('notes')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      return { error: error.message };
    }

    return { data: asNoteArray(data) };
  } catch {
    return { error: 'Failed to fetch notes' };
  }
}

export async function getNoteById(id: string): Promise<ServiceResult<Note>> {
  try {
    const { data, error } = await supabase
      .from('notes')
      .select('*')
      .eq('id', id)
      .maybeSingle();

    if (error) {
      return { error: error.message };
    }

    if (!data) {
      return { error: 'Note not found' };
    }

    return { data: asNote(data) };
  } catch {
    return { error: 'Failed to fetch note' };
  }
}

export async function createNote(noteData: NoteInsert): Promise<ServiceResult<Note>> {
  const validationErrors = validateNote(noteData);
  if (validationErrors.length > 0) {
    return { validationErrors };
  }

  try {
    const { data, error } = await supabase
      .from('notes')
      .insert(noteData)
      .select()
      .single();

    if (error) {
      return { error: error.message };
    }

    return { data: asNote(data) };
  } catch {
    return { error: 'Failed to create note' };
  }
}

export async function updateNote(id: string, noteData: NoteUpdate): Promise<ServiceResult<Note>> {
  const validationErrors = validateNote(noteData);
  if (validationErrors.length > 0) {
    return { validationErrors };
  }

  try {
    const { data, error } = await supabase
      .from('notes')
      .update(noteData)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      return { error: error.message };
    }

    return { data: asNote(data) };
  } catch {
    return { error: 'Failed to update note' };
  }
}

export async function deleteNote(id: string): Promise<ServiceResult<void>> {
  try {
    const { error } = await supabase
      .from('notes')
      .delete()
      .eq('id', id);

    if (error) {
      return { error: error.message };
    }

    return {};
  } catch {
    return { error: 'Failed to delete note' };
  }
}
