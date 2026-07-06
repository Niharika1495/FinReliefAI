import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { User, Lock, ShieldAlert } from 'lucide-react';
import { useState } from 'react';
import toast from 'react-hot-toast';
import { adminApi } from '@/api/admin';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const schema = z.object({
  username: z.string().min(1, 'Username is required'),
  password: z.string().min(1, 'Password is required'),
});

export default function AdminLoginPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { username: '', password: '' },
  });

  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      const res = await adminApi.login(data.username, data.password);
      const payload = res.data?.data || res.data;
      
      const token = payload.access_token;
      if (!token) {
        throw new Error('Access token missing in response');
      }

      localStorage.setItem('finrelief_admin_token', token);
      toast.success('Admin login successful!');
      navigate('/admin/dashboard');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Invalid administrator credentials');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-[#09101d] p-6 animate-fade-in">
      <Card padding="p-8" className="w-full max-w-[400px]">
        <div className="flex flex-col items-center gap-3 text-center mb-6">
          <div className="h-12 w-12 rounded-2xl bg-red-50 dark:bg-red-900/20 text-red-500 flex items-center justify-center">
            <ShieldAlert size={24} />
          </div>
          <div>
            <h2 className="text-xl font-bold text-surface-900 dark:text-surface-100">Admin Control Panel</h2>
            <p className="text-xs text-surface-500 dark:text-surface-400 mt-1">
              Sign in with your administrative credentials to manage system systems.
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" id="admin-login-form">
          <Input
            label="Username"
            leftIcon={User}
            placeholder="admin"
            error={errors.username?.message}
            id="admin-username-input"
            {...register('username')}
          />
          <Input
            label="Password"
            type="password"
            leftIcon={Lock}
            placeholder="••••••••"
            error={errors.password?.message}
            id="admin-password-input"
            {...register('password')}
          />

          <Button
            type="submit"
            size="lg"
            isLoading={isLoading}
            className="w-full mt-2"
            id="admin-login-submit"
          >
            Authenticate Admin
          </Button>
        </form>
      </Card>
    </div>
  );
}

// Minimal placeholder Card wrapper in case of local styling override
function Card({ children, className, padding = 'p-5' }) {
  return (
    <div className={`bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-2xl shadow-xl ${padding} ${className}`}>
      {children}
    </div>
  );
}
