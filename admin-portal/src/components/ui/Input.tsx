import React, { forwardRef } from 'react';

export type InputVariant = 'outlined' | 'filled';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: InputVariant;
  label?: string;
  helperText?: string;
  error?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      variant = 'outlined',
      label,
      helperText,
      error = false,
      icon,
      iconPosition = 'left',
      className = '',
      ...props
    },
    ref
  ) => {
    const variantClass = `md-input-${variant}`;
    const errorClass = error ? 'border-error-600 focus:border-error-600 focus:ring-error-200' : '';
    const iconClass = icon ? (iconPosition === 'left' ? 'pl-12' : 'pr-12') : '';

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            {label}
          </label>
        )}
        <div className="relative">
          {icon && iconPosition === 'left' && (
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-500">
              {icon}
            </div>
          )}
          <input
            ref={ref}
            className={`${variantClass} ${errorClass} ${iconClass} ${className}`}
            {...props}
          />
          {icon && iconPosition === 'right' && (
            <div className="absolute right-4 top-1/2 -translate-y-1/2 text-neutral-500">
              {icon}
            </div>
          )}
        </div>
        {helperText && (
          <p className={`mt-2 text-sm ${error ? 'text-error-600' : 'text-neutral-600'}`}>
            {helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
