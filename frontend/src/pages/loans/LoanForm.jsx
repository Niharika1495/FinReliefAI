import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useEffect } from 'react';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { Button } from '@/components/ui/Button';
import { LOAN_TYPES, LOAN_STATUSES } from '@/utils/constants';

// Zod schema aligned with backend LoanCreate and LoanUpdate schemas
const schema = z.object({
  lender_name: z.string().min(2, 'Lender name is required'),
  loan_type: z.string().min(1, 'Please select a loan type'),
  outstanding_amount: z.coerce.number().positive('Must be positive'),
  emi: z.coerce.number().positive('Must be positive'),
  interest_rate: z.coerce.number().min(0).max(100, 'Must be between 0–100'),
  overdue_months: z.coerce.number().int().min(0).optional().default(0),
  loan_status: z.string().min(1, 'Please select status'),
});

export function LoanForm({ initialValues, onSubmit, isLoading, onCancel }) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      lender_name: '',
      loan_type: '',
      outstanding_amount: '',
      emi: '',
      interest_rate: '',
      overdue_months: 0,
      loan_status: 'ACTIVE',
    },
  });

  useEffect(() => {
    if (initialValues) {
      reset({
        lender_name: initialValues.lender_name || '',
        loan_type: initialValues.loan_type || '',
        outstanding_amount: initialValues.outstanding_amount || '',
        emi: initialValues.emi || '',
        interest_rate: initialValues.interest_rate || '',
        overdue_months: initialValues.overdue_months || 0,
        loan_status: initialValues.loan_status || 'ACTIVE',
      });
    }
  }, [initialValues, reset]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" id="loan-form">
      <div className="grid grid-cols-2 gap-3">
        <div className="col-span-2">
          <Input
            label="Lender Name"
            placeholder="e.g. Chase Bank"
            error={errors.lender_name?.message}
            id="lender-name-input"
            {...register('lender_name')}
          />
        </div>
        
        <Select
          label="Loan Type"
          options={LOAN_TYPES}
          placeholder="Select type"
          error={errors.loan_type?.message}
          id="loan-type-select"
          {...register('loan_type')}
        />
        
        <Select
          label="Status"
          options={LOAN_STATUSES}
          placeholder="Select status"
          error={errors.loan_status?.message}
          id="loan-status-select"
          {...register('loan_status')}
        />
        
        <Input
          label="Outstanding Amount"
          type="number"
          placeholder="10000"
          error={errors.outstanding_amount?.message}
          id="outstanding-input"
          {...register('outstanding_amount')}
        />
        
        <Input
          label="Monthly EMI"
          type="number"
          placeholder="500"
          error={errors.emi?.message}
          id="emi-input"
          {...register('emi')}
        />
        
        <Input
          label="Interest Rate (%)"
          type="number"
          step="0.01"
          placeholder="8.5"
          error={errors.interest_rate?.message}
          id="interest-input"
          {...register('interest_rate')}
        />
        
        <Input
          label="Overdue Months"
          type="number"
          placeholder="0"
          error={errors.overdue_months?.message}
          id="overdue-input"
          {...register('overdue_months')}
        />
      </div>

      <div className="flex gap-3 justify-end pt-2">
        <Button type="button" variant="ghost" onClick={onCancel} id="loan-form-cancel">
          Cancel
        </Button>
        <Button type="submit" isLoading={isLoading} id="loan-form-submit">
          {initialValues ? 'Update Loan' : 'Add Loan'}
        </Button>
      </div>
    </form>
  );
}
