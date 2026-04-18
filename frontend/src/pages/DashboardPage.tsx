import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Sidebar from '../components/layout/Sidebar';
import { Plane, Shield, Fingerprint, Compass, User } from 'lucide-react';
// Shield and Fingerprint used in statCards below
import { useEffect, useState } from 'react';
import { GeneratedItinerary } from '../types';

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tripCount, setTripCount] = useState(0);

  useEffect(() => {
    const trips: GeneratedItinerary[] = JSON.parse(localStorage.getItem('voyonata_trips') || '[]');
    setTripCount(trips.length);
  }, []);

  const statCards = [
    {
      icon: Plane,
      iconBg: 'bg-indigo-500/20',
      iconColor: 'text-indigo-400',
      value: String(tripCount),
      label: 'Trips Planned',
    },
    {
      icon: Shield,
      iconBg: 'bg-emerald-500/20',
      iconColor: 'text-emerald-400',
      value: 'Active',
      label: 'Security Status',
    },
    {
      icon: Fingerprint,
      iconBg: 'bg-violet-500/20',
      iconColor: 'text-violet-400',
      value: '—',
      label: 'Passkeys Registered',
    },
  ];

  const actionCards = [
    {
      icon: Compass,
      iconBg: 'bg-orange-500/20',
      iconColor: 'text-orange-400',
      title: 'Plan a Trip',
      desc: 'Generate your perfect itinerary',
      to: '/plan',
    },
    {
      icon: User,
      iconBg: 'bg-emerald-500/20',
      iconColor: 'text-emerald-400',
      title: 'Edit Profile',
      desc: 'Update your name and email',
      to: '/profile',
    },
  ];

  return (
    <div className="flex min-h-screen bg-navy-900">
      <Sidebar />
      <main className="flex-1 p-8 overflow-y-auto">
        <div className="max-w-3xl">
          {/* Welcome */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-white mb-1">
              Welcome back,{' '}
              <span className="text-indigo-400">{user?.name}</span>
            </h1>
            <p className="text-slate-400 text-sm">
              Your secure travel command center. Plan your next adventure below.
            </p>
          </div>

          {/* Stat Cards */}
          <div className="grid grid-cols-3 gap-4 mb-8">
            {statCards.map(({ icon: Icon, iconBg, iconColor, value, label }) => (
              <div
                key={label}
                className="bg-navy-600 border border-navy-400 rounded-xl p-5"
              >
                <div className={`w-9 h-9 ${iconBg} rounded-lg flex items-center justify-center mb-4`}>
                  <Icon size={17} className={iconColor} />
                </div>
                <p className="text-2xl font-bold text-white leading-none mb-1">{value}</p>
                <p className="text-xs text-slate-400">{label}</p>
              </div>
            ))}
          </div>

          {/* Quick Actions */}
          <h2 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 gap-4">
            {actionCards.map(({ icon: Icon, iconBg, iconColor, title, desc, to }) => (
              <button
                key={title}
                onClick={() => navigate(to)}
                className="bg-navy-600 border border-navy-400 rounded-xl p-5 text-left hover:border-indigo-500/40 hover:bg-navy-500 transition-all group"
              >
                <div className={`w-9 h-9 ${iconBg} rounded-lg flex items-center justify-center mb-4`}>
                  <Icon size={17} className={iconColor} />
                </div>
                <p className="font-medium text-white text-sm group-hover:text-indigo-300 transition-colors">
                  {title}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
