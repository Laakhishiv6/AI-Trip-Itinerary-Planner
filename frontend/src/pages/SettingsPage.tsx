import Sidebar from '../components/layout/Sidebar';
import { Shield, Key, Bell } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen bg-navy-900">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="max-w-lg">
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-white mb-1">Settings</h1>
            <p className="text-slate-400 text-sm">Manage your account security and preferences.</p>
          </div>

          <div className="space-y-4">
            {[
              { icon: Shield, title: 'Security Status', desc: 'Your account is protected by Argon2 + FIDO2.', status: 'Active', statusColor: 'text-emerald-400' },
              { icon: Key, title: 'Passkeys', desc: 'Register hardware security keys for passwordless login.', status: 'Not configured', statusColor: 'text-slate-500' },
              { icon: Bell, title: 'Notifications', desc: 'Manage email and push notification preferences.', status: 'All enabled', statusColor: 'text-indigo-400' },
            ].map(({ icon: Icon, title, desc, status, statusColor }) => (
              <div key={title} className="bg-navy-600 border border-navy-400 rounded-xl p-5 flex items-center justify-between">
                <div className="flex items-start gap-4">
                  <div className="w-9 h-9 bg-navy-500 rounded-lg flex items-center justify-center">
                    <Icon size={16} className="text-slate-400" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">{title}</p>
                    <p className="text-slate-500 text-xs mt-0.5">{desc}</p>
                  </div>
                </div>
                <span className={`text-xs font-medium ${statusColor}`}>{status}</span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
