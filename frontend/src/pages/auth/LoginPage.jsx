import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { cn } from '@/utils/cn';

// Schema validates only email + password — matches backend LoginRequest exactly
const schema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '' },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      // Sends only { email, password } — no extra fields
      await login(data.email, data.password);
      toast.success('Welcome back!');
      navigate('/dashboard');
    } catch (err) {
      // Handle 400, 401, 422, 500 without crashing
      const response = err?.response;
      const status = response?.status;
      const detail = response?.data?.detail;

      if (status === 401) {
        toast.error('Invalid email or password. Please try again.');
      } else if (status === 423) {
        toast.error('Account locked due to too many failed attempts. Try again later.');
      } else if (status === 422 && Array.isArray(detail)) {
        const firstError = detail[0];
        const msg = firstError?.msg || 'Validation error';
        toast.error(msg);
      } else if (typeof detail === 'string') {
        toast.error(detail);
      } else {
        toast.error('Login failed. Please check your credentials.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">Sign in</h2>
        <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
          Don't have an account?{' '}
          <Link to="/register" className="font-medium text-primary-600 dark:text-primary-400 hover:underline">
            Create one free
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" id="login-form">
        <Input
          label="Email address"
          type="email"
          leftIcon={Mail}
          placeholder="you@example.com"
          error={errors.email?.message}
          id="email-input"
          autoComplete="email"
          {...register('email')}
        />

        {/* Password field with toggle — using a wrapper div approach */}
        <div className="flex flex-col gap-1.5">
          <label htmlFor="password-input" className="text-sm font-medium text-surface-700 dark:text-surface-300">
            Password
          </label>
          <div className="relative">
            <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
            <input
              id="password-input"
              type={showPassword ? 'text' : 'password'}
              placeholder="••••••••"
              autoComplete="current-password"
              className={cn(
                'w-full rounded-xl border bg-white dark:bg-surface-800 text-surface-900 dark:text-surface-100 placeholder-surface-400 dark:placeholder-surface-500',
                'pl-9 pr-11 py-2.5 text-sm transition-all duration-150',
                'border-surface-300 dark:border-surface-600',
                'focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500',
                errors.password && 'border-red-500 focus:ring-red-500/40'
              )}
              {...register('password')}
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
              tabIndex={-1}
              aria-label={showPassword ? 'Hide password' : 'Show password'}
              id="password-toggle"
            >
              {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {errors.password && (
            <p className="text-xs text-red-500">{errors.password.message}</p>
          )}
        </div>

        <Button
          type="submit"
          size="lg"
          isLoading={isLoading}
          className="w-full mt-2"
          id="login-submit"
        >
          Sign in to FinRelief AI
        </Button>
      </form>

      <div className="text-center text-xs text-surface-400 dark:text-surface-500">
        By signing in, you agree to our{' '}
        <span className="text-primary-500 cursor-pointer hover:underline">Terms of Service</span>
        {' '}and{' '}
        <span className="text-primary-500 cursor-pointer hover:underline">Privacy Policy</span>
      </div>
    </div>
  );
}
