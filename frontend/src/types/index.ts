export interface User {
  name: string;
  email: string;
}

export type BudgetType = 'Budget' | 'Moderate' | 'Luxury';

export interface TripParams {
  destination: string;
  startDate: string;
  endDate: string;
  travelers: number;
  budget: BudgetType;
  activities: string[];
  foodPreferences: string[];
}

export interface Activity {
  time: string;
  name: string;
  description: string;
  category: string;
}

export interface DayItinerary {
  day: number;
  dateStr: string;
  title: string;
  activities: Activity[];
}

export interface GeneratedItinerary {
  id: string;
  destination: string;
  startDate: string;
  endDate: string;
  numDays: number;
  travelers: number;
  budget: BudgetType;
  tags: string[];
  schedule: DayItinerary[];
}
