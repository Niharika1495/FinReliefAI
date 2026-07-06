import { Outlet } from 'react-router-dom';
import { TrendingUp, Shield, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';

const FEATURES = [
  { icon: TrendingUp, label: 'Financial Health Score', desc: 'Real-time credit & debt analysis' },
  { icon: BarChart3, label: 'AI-Powered Insights', desc: 'Smart recommendations for debt relief' },
  { icon: Shield, label: 'Bank-grade Security', desc: 'Your data is always protected' },
];

export function AuthLayout() {
  return (
    <div className="min-h-screen flex bg-surface-50 dark:bg-[#09101d]">
      {/* Left brand panel */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-[55%] flex-col justify-between bg-gradient-to-br from-primary-600 via-primary-700 to-[#4c1d95] p-12 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-20%] right-[-10%] w-96 h-96 rounded-full bg-white/5" />
          <div className="absolute bottom-[-10%] left-[-5%] w-80 h-80 rounded-full bg-teal-500/10" />
          <div className="absolute top-[40%] right-[20%] w-32 h-32 rounded-full bg-white/5" />
        </div>

        {/* Brand */}
        <div className="relative flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center">
            <TrendingUp size={22} className="text-white" />
          </div>
          <div>
            <p className="text-xl font-bold text-white">FinRelief AI</p>
            <p className="text-xs text-primary-200">AI-Powered Financial Recovery</p>
          </div>
        </div>

        {/* Headline */}
        <div className="relative space-y-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl xl:text-5xl font-bold text-white leading-tight">
              Take control of<br />
              <span className="text-teal-300">your financial future</span>
            </h1>
            <p className="text-lg text-primary-200 mt-4 max-w-md leading-relaxed">
              AI-powered debt relief, settlement recommendations, and financial health monitoring — all in one platform.
            </p>
          </motion.div>

          <div className="space-y-4">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.1, duration: 0.4 }}
                className="flex items-center gap-3"
              >
                <div className="h-9 w-9 rounded-lg bg-white/15 flex items-center justify-center flex-shrink-0">
                  <f.icon size={18} className="text-white" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{f.label}</p>
                  <p className="text-xs text-primary-200">{f.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <p className="relative text-xs text-primary-300">© 2025 FinRelief AI. All rights reserved.</p>
      </div>

      {/* Right: auth form */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-[420px]"
        >
          {/* Mobile brand */}
          <div className="flex items-center gap-2.5 mb-8 lg:hidden">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary-500 to-teal-500 flex items-center justify-center">
              <TrendingUp size={16} className="text-white" />
            </div>
            <p className="text-lg font-bold text-surface-900 dark:text-surface-100">FinRelief AI</p>
          </div>
          <Outlet />
        </motion.div>
      </div>
    </div>
  );
}
