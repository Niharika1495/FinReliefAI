import { Modal } from './Modal';
import { Button } from './Button';
import { AlertTriangle } from 'lucide-react';

export function ConfirmDialog({
  isOpen, onClose, onConfirm, isLoading,
  title = 'Are you sure?',
  message = 'This action cannot be undone.',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  variant = 'danger',
}) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="sm">
      <div className="flex flex-col items-center text-center gap-4">
        <div className={`h-12 w-12 rounded-full flex items-center justify-center ${
          variant === 'danger'
            ? 'bg-red-100 dark:bg-red-900/20'
            : 'bg-amber-100 dark:bg-amber-900/20'
        }`}>
          <AlertTriangle size={22} className={variant === 'danger' ? 'text-red-500' : 'text-amber-500'} />
        </div>
        <div>
          <h3 className="text-base font-semibold text-surface-900 dark:text-surface-100 mb-1">{title}</h3>
          <p className="text-sm text-surface-500 dark:text-surface-400">{message}</p>
        </div>
        <div className="flex gap-3 w-full">
          <Button
            variant="ghost"
            className="flex-1"
            onClick={onClose}
            disabled={isLoading}
            id="confirm-dialog-cancel"
          >
            {cancelLabel}
          </Button>
          <Button
            variant={variant}
            className="flex-1"
            onClick={onConfirm}
            isLoading={isLoading}
            id="confirm-dialog-confirm"
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
