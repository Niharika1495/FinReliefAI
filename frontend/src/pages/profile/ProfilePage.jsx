import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { profileApi } from '@/api/profile';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader } from '@/components/ui/Card';
import { StatCard } from '@/components/ui/StatCard';
import { SkeletonCard } from '@/components/ui/Skeleton';
import { formatCurrency, formatPercent } from '@/utils/formatters';
import { IndianRupee, User, Save, TrendingUp, Activity, RefreshCw } from 'lucide-react';

const schema = z.object({
  monthly_income: z.coerce.number().positive('Monthly income must be positive'),
  monthly_expenses: z.coerce.number().positive('Monthly expenses must be positive'),
});

export default function ProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);

  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: { monthly_income: '', monthly_expenses: '' },
  });

  const income = watch('monthly_income');
  const expenses = watch('monthly_expenses');
  const surplus = income && expenses ? Number(income) - Number(expenses) : null;

  const fetchProfile = async () => {
    setIsLoading(true);
    try {
      const res = await profileApi.getProfile();
      const d = res.data;
      const p = d.data || d;
      setProfile(p);
      setHasProfile(true);
      reset({
        monthly_income: p.monthly_income || '',
        monthly_expenses: p.monthly_expenses || '',
      });
    } catch (err) {
      if (err?.response?.status === 404) {
        setHasProfile(false);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { fetchProfile(); }, []);

  const onSubmit = async (data) => {
    setIsSaving(true);
    try {
      let res;
      if (hasProfile) {
        res = await profileApi.updateProfile(data);
      } else {
        res = await profileApi.createProfile(data);
        setHasProfile(true);
      }
      const d = res.data;
      setProfile(d.data || d);
      toast.success('Profile saved successfully!');
    } catch (err) {
      toast.error(err?.response?.data?.detail || 'Failed to save profile');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-3xl">
        <SkeletonCard />
        <SkeletonCard />
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in max-w-3xl">
      <div>
        <h1 className="text-xl font-bold text-surface-900 dark:text-surface-100">Financial Profile</h1>
        <p className="text-sm text-surface-500 dark:text-surface-400 mt-0.5">
          Manage your income and expenses to power your financial analysis.
        </p>
      </div>

      {/* Account info */}
      <Card padding="p-5">
        <CardHeader title="Account Information" />
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center text-white text-xl font-bold flex-shrink-0">
            {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
          </div>
          <div>
            <p className="text-base font-semibold text-surface-900 dark:text-surface-100">{user?.name || 'User'}</p>
            <p className="text-sm text-surface-500 dark:text-surface-400">{user?.email}</p>
          </div>
        </div>
      </Card>

      {/* Profile form */}
      <Card padding="p-5">
        <CardHeader
          title="Financial Details"
          subtitle="Used for analysis and settlement calculations"
        />
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" id="profile-form">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Monthly Income"
              type="number"
              leftIcon={IndianRupee}
              placeholder="5000"
              error={errors.monthly_income?.message}
              id="profile-income-input"
              {...register('monthly_income')}
            />
            <Input
              label="Monthly Expenses"
              type="number"
              leftIcon={IndianRupee}
              placeholder="2000"
              error={errors.monthly_expenses?.message}
              id="profile-expenses-input"
              {...register('monthly_expenses')}
            />
          </div>

          {/* Live preview */}
          {income && expenses && (
            <div className={`rounded-xl p-3 text-sm flex items-center justify-between ${
              surplus >= 0
                ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400'
                : 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400'
            }`}>
              <span>Monthly Surplus</span>
              <span className="font-bold">{formatCurrency(surplus)}</span>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="ghost" onClick={fetchProfile} id="profile-reset">
              <RefreshCw size={14} /> Reset
            </Button>
            <Button type="submit" isLoading={isSaving} id="profile-save">
              <Save size={14} /> {hasProfile ? 'Update Profile' : 'Save Profile'}
            </Button>
          </div>
        </form>
      </Card>

      {/* Metrics from saved profile */}
      {profile && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <StatCard
            title="Monthly Income"
            value={formatCurrency(profile.monthly_income)}
            icon={TrendingUp}
            color="emerald"
          />
          <StatCard
            title="Monthly Expenses"
            value={formatCurrency(profile.monthly_expenses)}
            icon={Activity}
            color="amber"
          />
          <StatCard
            title="Net Surplus"
            value={formatCurrency(profile.monthly_income - profile.monthly_expenses)}
            icon={IndianRupee}
            color={(profile.monthly_income - profile.monthly_expenses) >= 0 ? 'teal' : 'red'}
          />
        </div>
      )}
    </div>
  );
}
