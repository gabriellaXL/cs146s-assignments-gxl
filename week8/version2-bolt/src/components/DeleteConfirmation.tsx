import { AlertTriangle } from 'lucide-react';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';

interface DeleteConfirmationProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  isDeleting: boolean;
}

export function DeleteConfirmation({
  isOpen,
  onClose,
  onConfirm,
  title,
  isDeleting,
}: DeleteConfirmationProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Delete Note">
      <div className="space-y-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <p className="text-gray-900 font-medium mb-2">
              Are you sure you want to delete this note?
            </p>
            <p className="text-gray-700 mb-1">
              <span className="font-semibold">"{title}"</span>
            </p>
            <p className="text-gray-600 text-sm">
              This action cannot be undone.
            </p>
          </div>
        </div>

        <div className="flex gap-3 pt-4">
          <Button
            variant="danger"
            onClick={onConfirm}
            disabled={isDeleting}
            className="flex-1"
          >
            {isDeleting ? 'Deleting...' : 'Delete Note'}
          </Button>
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isDeleting}
          >
            Cancel
          </Button>
        </div>
      </div>
    </Modal>
  );
}
