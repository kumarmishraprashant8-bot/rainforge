/**
 * Form Validation Hook
 * Real-time validation with helpful error messages
 */

import { useState, useCallback, useMemo } from 'react';

type ValidationRule = {
    validate: (value: any, formValues?: Record<string, any>) => boolean;
    message: string;
};

type FieldConfig = {
    rules: ValidationRule[];
    required?: boolean;
};

type FormConfig = Record<string, FieldConfig>;

type FormErrors = Record<string, string>;
type FormTouched = Record<string, boolean>;

export function useFormValidation<T extends Record<string, any>>(
    initialValues: T,
    config: FormConfig
) {
    const [values, setValues] = useState<T>(initialValues);
    const [errors, setErrors] = useState<FormErrors>({});
    const [touched, setTouched] = useState<FormTouched>({});
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Validate a single field
    const validateField = useCallback((name: string, value: any): string => {
        const fieldConfig = config[name];
        if (!fieldConfig) return '';

        // Check required
        if (fieldConfig.required && !value && value !== 0) {
            return 'This field is required';
        }

        // Check custom rules
        for (const rule of fieldConfig.rules) {
            if (!rule.validate(value, values)) {
                return rule.message;
            }
        }

        return '';
    }, [config, values]);

    // Validate all fields
    const validateAll = useCallback((): boolean => {
        const newErrors: FormErrors = {};
        let isValid = true;

        for (const [name, fieldConfig] of Object.entries(config)) {
            const error = validateField(name, values[name as keyof T]);
            if (error) {
                newErrors[name] = error;
                isValid = false;
            }
        }

        setErrors(newErrors);
        return isValid;
    }, [config, validateField, values]);

    // Handle field change
    const handleChange = useCallback((name: keyof T) => (
        e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
    ) => {
        const value = e.target.type === 'checkbox'
            ? (e.target as HTMLInputElement).checked
            : e.target.value;

        setValues(prev => ({ ...prev, [name]: value }));

        // Validate on change if already touched
        if (touched[name as string]) {
            const error = validateField(name as string, value);
            setErrors(prev => ({ ...prev, [name]: error }));
        }
    }, [touched, validateField]);

    // Handle field blur
    const handleBlur = useCallback((name: keyof T) => () => {
        setTouched(prev => ({ ...prev, [name]: true }));
        const error = validateField(name as string, values[name]);
        setErrors(prev => ({ ...prev, [name]: error }));
    }, [validateField, values]);

    // Set a field value programmatically
    const setValue = useCallback((name: keyof T, value: any) => {
        setValues(prev => ({ ...prev, [name]: value }));
    }, []);

    // Reset form
    const reset = useCallback(() => {
        setValues(initialValues);
        setErrors({});
        setTouched({});
        setIsSubmitting(false);
    }, [initialValues]);

    // Handle form submission
    const handleSubmit = useCallback((onSubmit: (values: T) => Promise<void> | void) =>
        async (e: React.FormEvent) => {
            e.preventDefault();

            // Mark all fields as touched
            const allTouched: FormTouched = {};
            Object.keys(config).forEach(key => { allTouched[key] = true; });
            setTouched(allTouched);

            if (!validateAll()) {
                return;
            }

            setIsSubmitting(true);
            try {
                await onSubmit(values);
            } finally {
                setIsSubmitting(false);
            }
        },
        [config, validateAll, values]);

    // Field props helper
    const getFieldProps = useCallback((name: keyof T) => ({
        name,
        value: values[name] || '',
        onChange: handleChange(name),
        onBlur: handleBlur(name),
    }), [values, handleChange, handleBlur]);

    // Field state helper
    const getFieldState = useCallback((name: keyof T) => ({
        error: errors[name as string],
        touched: touched[name as string],
        hasError: touched[name as string] && !!errors[name as string],
    }), [errors, touched]);

    // Form validity
    const isValid = useMemo(() => Object.values(errors).every(e => !e), [errors]);

    return {
        values,
        errors,
        touched,
        isSubmitting,
        isValid,
        handleChange,
        handleBlur,
        handleSubmit,
        setValue,
        setValues,
        reset,
        validateField,
        validateAll,
        getFieldProps,
        getFieldState,
    };
}

// Common validation rules
export const validationRules = {
    email: {
        validate: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
        message: 'Please enter a valid email address',
    },
    phone: {
        validate: (value: string) => /^[6-9]\d{9}$/.test(value.replace(/\D/g, '')),
        message: 'Please enter a valid 10-digit mobile number',
    },
    pincode: {
        validate: (value: string) => /^\d{6}$/.test(value),
        message: 'Please enter a valid 6-digit PIN code',
    },
    minLength: (min: number) => ({
        validate: (value: string) => value.length >= min,
        message: `Must be at least ${min} characters`,
    }),
    maxLength: (max: number) => ({
        validate: (value: string) => value.length <= max,
        message: `Must be no more than ${max} characters`,
    }),
    min: (min: number) => ({
        validate: (value: number) => value >= min,
        message: `Must be at least ${min}`,
    }),
    max: (max: number) => ({
        validate: (value: number) => value <= max,
        message: `Must be no more than ${max}`,
    }),
    pattern: (regex: RegExp, message: string) => ({
        validate: (value: string) => regex.test(value),
        message,
    }),
};

// Form field component with validation display
export const FormField: React.FC<{
    label: string;
    name: string;
    type?: string;
    placeholder?: string;
    error?: string;
    touched?: boolean;
    hint?: string;
    children?: React.ReactNode;
}> = ({ label, name, type = 'text', placeholder, error, touched, hint, children }) => {
    const hasError = touched && error;

    return (
        <div className="space-y-1">
            <label htmlFor={name} className="block text-sm font-medium text-gray-300">
                {label}
            </label>
            {children || (
                <input
                    type={type}
                    id={name}
                    name={name}
                    placeholder={placeholder}
                    className={`w-full px-4 py-3 bg-white/5 border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 transition-all ${hasError
                            ? 'border-red-500 focus:ring-red-500/50'
                            : 'border-white/10 focus:ring-cyan-500/50 focus:border-cyan-500/50'
                        }`}
                />
            )}
            {hasError ? (
                <p className="text-red-400 text-xs mt-1 animate-fade-in">{error}</p>
            ) : hint ? (
                <p className="text-gray-500 text-xs mt-1">{hint}</p>
            ) : null}
        </div>
    );
};

export default useFormValidation;
