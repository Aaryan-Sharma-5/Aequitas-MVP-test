/**
 * TypeScript types for deal management
 */

export type DealStatus = 'potential' | 'ongoing' | 'completed' | 'rejected';

export interface Deal {
  // Primary Key
  id?: number;

  // Basic Deal Information
  dealName: string;
  location: string;
  status: DealStatus;
  createdAt?: string;
  updatedAt?: string;

  // Property Information
  propertyAddress?: string;
  latitude?: number;
  longitude?: number;

  // Purchase Details
  purchasePrice?: number;
  downPaymentPercent?: number;
  loanInterestRate?: number;
  loanTermYears?: number;
  closingCosts?: number;

  // Income
  monthlyRent?: number;
  otherMonthlyIncome?: number;
  vacancyRate?: number;
  annualRentIncrease?: number;

  // Expenses
  propertyTaxAnnual?: number;
  insuranceAnnual?: number;
  hoaMonthly?: number;
  maintenancePercent?: number;
  propertyManagementPercent?: number;
  utilitiesMonthly?: number;
  otherExpensesMonthly?: number;

  // Property Details
  bedrooms?: number;
  bathrooms?: number;
  squareFootage?: number;
  propertyType?: string;
  yearBuilt?: number;

  // Market Data Snapshots (JSON strings)
  rentcastData?: string;
  fredData?: string;

  // Calculated Metrics
  monthlyPayment?: number;
  totalMonthlyIncome?: number;
  totalMonthlyExpenses?: number;
  monthlyCashFlow?: number;
  cashOnCashReturn?: number;
  capRate?: number;
  roi?: number;
  npv?: number;
  irr?: number;
}

export interface DealFormData {
  dealName: string;
  location: string;
  status: DealStatus;
  propertyAddress?: string;
  latitude?: number;
  longitude?: number;
}

export interface DealResponse {
  deal: Deal;
}

export interface DealsListResponse {
  deals: Deal[];
}

export interface DealsGroupedResponse {
  potential: Deal[];
  ongoing: Deal[];
  completed: Deal[];
  rejected: Deal[];
}

export interface DealDeleteResponse {
  success: boolean;
  message: string;
}

export interface ApiError {
  error: string;
}

export const DEAL_STATUS_LABELS: Record<DealStatus, string> = {
  potential: 'Potential',
  ongoing: 'Ongoing',
  completed: 'Completed',
  rejected: 'Rejected'
};

export const DEAL_STATUS_COLORS: Record<DealStatus, { bg: string; text: string; border: string }> = {
  potential: {
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200'
  },
  ongoing: {
    bg: 'bg-yellow-50',
    text: 'text-yellow-700',
    border: 'border-yellow-200'
  },
  completed: {
    bg: 'bg-green-50',
    text: 'text-green-700',
    border: 'border-green-200'
  },
  rejected: {
    bg: 'bg-red-50',
    text: 'text-red-700',
    border: 'border-red-200'
  }
};
