import React from 'react';
import { motion } from 'framer-motion';

export type CardVariant = 'filled' | 'elevated' | 'outlined';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant;
  interactive?: boolean;
  padding?: 'none' | 'small' | 'medium' | 'large';
}

const paddingClasses = {
  none: 'p-0',
  small: 'p-4',
  medium: 'p-6',
  large: 'p-8',
};

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'elevated',
  interactive = false,
  padding = 'medium',
  className = '',
  ...props
}) => {
  const variantClass = `md-card-${variant}`;
  const paddingClass = paddingClasses[padding];
  const interactiveClass = interactive ? 'cursor-pointer' : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={interactive ? { y: -4, scale: 1.01 } : {}}
      className={`${variantClass} ${paddingClass} ${interactiveClass} ${className}`}
      {...props}
    >
      {children}
    </motion.div>
  );
};

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  action,
  className = '',
  ...props
}) => {
  return (
    <div className={`flex items-start justify-between mb-4 ${className}`} {...props}>
      <div>
        <h3 className="text-xl font-semibold text-neutral-900">{title}</h3>
        {subtitle && <p className="text-sm text-neutral-600 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
};

export const CardContent: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div className={className} {...props}>
      {children}
    </div>
  );
};

export const CardFooter: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  children,
  className = '',
  ...props
}) => {
  return (
    <div className={`mt-4 pt-4 border-t border-neutral-200 ${className}`} {...props}>
      {children}
    </div>
  );
};
