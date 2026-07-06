import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { Mail, Lock, User, DollarSign } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { authApi } from '@/api/auth';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

// Schema uses `name` to match backend RegisterRequest exactly
const schema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  monthly_income: z.coerce.number().positive('Monthly income must be positive'),
  monthly_expenses: z.coerce.number().positive('Monthly expenses must be positive'),
});

export default function RegisterPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      name: '',
      email: '',
      password: '',
      monthly_income: '',
      monthly_expenses: '',
    },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      // Payload matches backend exactly: { name, email, password, monthly_income, monthly_expenses }
      await authApi.register({
        name: data.name,
        email: data.email,
        password: data.password,
        monthly_income: data.monthly_income,
        monthly_expenses: data.monthly_expenses,
      });

      // Auto-login after successful registration
      await login(data.email, data.password);
      toast.success('Account created! Welcome to FinRelief AI.');
      navigate('/dashboard');
    } catch (err) {
      // Handle 400, 401, 422, 500 without crashing
      const response = err?.response;
      const status = response?.status;
      const detail = response?.data?.detail;

      if (status === 422 && Array.isArray(detail)) {
        // FastAPI validation error — show first message
        const firstError = detail[0];
        const field = firstError?.loc?.slice(-1)[0] || 'field';
        const msg = firstError?.msg || 'Validation error';
        toast.error(`${field}: ${msg}`);
      } else if (typeof detail === 'string') {
        toast.error(detail);
      } else if (status === 400) {
        toast.error(response?.data?.message || 'Registration failed. Email may already be in use.');
      } else {
        toast.error('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-surface-900 dark:text-surface-100">Create your account</h2>
        <p className="mt-2 text-sm text-surface-500 dark:text-surface-400">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-primary-600 dark:text-primary-400 hover:underline">
            Sign in
          </Link>
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" id="register-form">
        <Input
          label="Full name"
          leftIcon={User}
          placeholder="John Doe"
          error={errors.name?.message}
          id="fullname-input"
          {...register('name')}
        />
        <Input
          label="Email address"
          type="email"
          leftIcon={Mail}
          placeholder="you@example.com"
          error={errors.email?.message}
          id="register-email-input"
          {...register('email')}
        />
        <Input
          label="Password"
          type="password"
          leftIcon={Lock}
          placeholder="Min. 6 characters"
          error={errors.password?.message}
          id="register-password-input"
          {...register('password')}
        />

        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Monthly Income"
            type="number"
            leftIcon={DollarSign}
            placeholder="5000"
            error={errors.monthly_income?.message}
            id="income-input"
            {...register('monthly_income')}
          />
          <Input
            label="Monthly Expenses"
            type="number"
            leftIcon={DollarSign}
            placeholder="2000"
            error={errors.monthly_expenses?.message}
            id="expenses-input"
            {...register('monthly_expenses')}
          />
        </div>

        <Button
          type="submit"
          size="lg"
          isLoading={isLoading}
          className="w-full mt-2"
          id="register-submit"
        >
          Create Account
        </Button>
      </form>
    </div>
  );
}
