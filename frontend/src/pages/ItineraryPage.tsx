import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import Sidebar from '../components/layout/Sidebar';
import { GeneratedItinerary, Activity } from '../types';
import { ArrowLeft, Trash2, MapPin, Calendar, Users, Wallet, Clock, Utensils } from 'lucide-react';

const categoryColors: Record<string, string> = {
  Travel: 'bg-blue-500/15 text-blue-300 border-blue-500/25',
  Culture: 'bg-amber-500/15 text-amber-300 border-amber-500/25',
  Beaches: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/25',
  Nightlife: 'bg-violet-500/15 text-violet-300 border-violet-500/25',
  Adventure: 'bg-orange-500/15 text-orange-300 border-orange-500/25',
  Zoo: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
  Shopping: 'bg-pink-500/15 text-pink-300 border-pink-500/25',
  'Food & Dining': 'bg-rose-500/15 text-rose-300 border-rose-500/25',
  Nature: 'bg-green-500/15 text-green-300 border-green-500/25',
  Wellness: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/25',
  Photography: 'bg-purple-500/15 text-purple-300 border-purple-500/25',
};

const tagColors = [
  'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
  'bg-violet-500/20 text-violet-300 border-violet-500/30',
  'bg-blue-500/20 text-blue-300 border-blue-500/30',
  'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
  'bg-amber-500/20 text-amber-300 border-amber-500/30',
];

function ActivityRow({ activity, isLast }: { activity: Activity; isLast: boolean }) {
  const colorClass = categoryColors[activity.category] || 'bg-slate-500/15 text-slate-300 border-slate-500/25';
  const isFood = activity.category === 'Food & Dining';

  return (
    <div className="flex gap-4">
      <div className="flex flex-col items-center">
        <div className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 z-10 ${isFood ? 'bg-rose-400' : 'bg-indigo-500'}`} />
        {!isLast && <div className="w-px flex-1 bg-navy-400 mt-1" />}
      </div>
      <div className={`flex-1 min-w-0 ${isLast ? 'pb-2' : 'pb-6'}`}>
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <span className="text-xs text-slate-500 flex items-center gap-1 mb-1">
              {isFood ? <Utensils size={10} /> : <Clock size={10} />}
              {activity.time}
            </span>
            <p className="text-white font-medium text-sm leading-snug">{activity.name}</p>
            <p className="text-slate-400 text-xs mt-0.5 leading-relaxed">{activity.description}</p>
          </div>
          <span className={`px-2 py-0.5 rounded-full text-xs border shrink-0 mt-1 ${colorClass}`}>
            {activity.category}
          </span>
        </div>
      </div>
    </div>
  );
}

export default function ItineraryPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [trip, setTrip] = useState<GeneratedItinerary | null>(null);
  const [activeDay, setActiveDay] = useState(0);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    const trips: GeneratedItinerary[] = JSON.parse(localStorage.getItem('voyonata_trips') || '[]');
    const found = trips.find(t => t.id === id);
    if (found) {
      setTrip(found);
    } else {
      navigate('/trips');
    }
  }, [id, navigate]);

  const handleDelete = () => {
    const trips: GeneratedItinerary[] = JSON.parse(localStorage.getItem('voyonata_trips') || '[]');
    localStorage.setItem('voyonata_trips', JSON.stringify(trips.filter(t => t.id !== id)));
    navigate('/trips');
  };

  if (!trip) {
    return (
      <div className="flex min-h-screen bg-navy-900">
        <Sidebar />
        <main className="flex-1 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
        </main>
      </div>
    );
  }

  const currentDay = trip.schedule[activeDay];

  return (
    <div className="flex min-h-screen bg-navy-900">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-8 py-8">
          {/* Top bar */}
          <div className="flex items-center justify-between mb-7">
            <button
              onClick={() => navigate('/trips')}
              className="flex items-center gap-1.5 text-slate-400 hover:text-slate-200 text-sm transition-colors"
            >
              <ArrowLeft size={15} />
              Back to Trips
            </button>

            {showDeleteConfirm ? (
              <div className="flex items-center gap-2">
                <span className="text-slate-400 text-xs">Delete this trip?</span>
                <button
                  onClick={handleDelete}
                  className="px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-medium rounded-lg transition-colors"
                >
                  Yes, Delete
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-3 py-1.5 bg-navy-500 hover:bg-navy-400 text-slate-300 text-xs font-medium rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </div>
            ) : (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center gap-1.5 text-slate-500 hover:text-red-400 text-sm transition-colors"
              >
                <Trash2 size={14} />
                Delete Trip
              </button>
            )}
          </div>

          {/* Destination */}
          <div className="mb-5">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full" />
              <h1 className="text-2xl font-bold text-white">{trip.destination}</h1>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-slate-400 text-xs mb-4">
              <span className="flex items-center gap-1.5">
                <Calendar size={12} />
                {trip.startDate} – {trip.endDate}
              </span>
              <span className="flex items-center gap-1.5">
                <MapPin size={12} />
                {trip.numDays} day{trip.numDays !== 1 ? 's' : ''}
              </span>
              <span className="flex items-center gap-1.5">
                <Users size={12} />
                {trip.travelers} traveler{trip.travelers > 1 ? 's' : ''}
              </span>
              <span className="flex items-center gap-1.5">
                <Wallet size={12} />
                {trip.budget}
              </span>
            </div>

            <div className="flex flex-wrap gap-1.5">
              {trip.tags.map((tag, i) => (
                <span
                  key={tag}
                  className={`px-3 py-1 rounded-full text-xs border font-medium ${tagColors[i % tagColors.length]}`}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Day tabs */}
          <div className="flex gap-0 overflow-x-auto border-b border-navy-400 mb-6">
            {trip.schedule.map((day, idx) => (
              <button
                key={day.day}
                onClick={() => setActiveDay(idx)}
                className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap transition-all border-b-2 -mb-px ${
                  activeDay === idx
                    ? 'text-indigo-400 border-indigo-500 bg-indigo-600/10'
                    : 'text-slate-500 border-transparent hover:text-slate-300 hover:bg-navy-600'
                }`}
              >
                Day {day.day}
              </button>
            ))}
          </div>

          {/* Day content */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-white font-semibold">{currentDay.title}</h2>
              <span className="text-slate-500 text-xs">{currentDay.dateStr}</span>
            </div>

            <div>
              {currentDay.activities.map((activity, idx) => (
                <ActivityRow
                  key={idx}
                  activity={activity}
                  isLast={idx === currentDay.activities.length - 1}
                />
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
