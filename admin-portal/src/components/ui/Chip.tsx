import React from 'react';
import { X } from 'lucide-react';

export type ChipVariant = 'assist' | 'filter' | 'input' | 'suggestion';

interface ChipProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: ChipVariant;
  selected?: boolean;
  onDelete?: () => void;
  icon?: React.ReactNode;
}

const variantClasses = {
  assist: 'md-chip-assist',
  filter: 'md-chip-filter',
  input: 'md-chip',
  suggestion: 'md-chip',
};

export const Chip: React.FC<ChipProps> = ({
  children,
  variant = 'assist',
  selected = false,
  onDelete,
  icon,
  className = '',
  ...props
}) => {
  const baseClass = selected && variant === 'filter' ? 'md-chip-filter-selected' : variantClasses[variant];

  return (
    <div
      className={`${baseClass} ${className}`}
      {...props}
    >
      {icon && <span>{icon}</span>}
      <span>{children}</span>
      {onDelete && (
        <button
          onClick={onDelete}
          className="ml-1 hover:bg-neutral-300 rounded-full p-0.5 transition-colors"
          aria-label="Remove"
        >
          <X size={14} />
        </button>
      )}
    </div>
  );
};
