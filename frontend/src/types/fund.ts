/**
 * TypeScript type definitions for Fund data
 */

export interface Fund {
  id?: number;
  fundName: string;
  fundSize: number;
  vintageYear: number;
  status: string;
  investmentPeriodStart?: string;
  investmentPeriodEnd?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface FundMetrics {
  id?: number;
  fundId: number;
  asOfDate: string;
  deployedCapital: number;
  remainingCapital: number;
  netIrr: number;
  tvpi: number;
  dpi: number;
  totalValue: number;
  createdAt?: string;
}

export interface QuarterlyPerformance {
  id?: number;
  fundId: number;
  year: number;
  quarter: number;
  quarterLabel: string;
  irr: number;
  createdAt?: string;
}

export interface InvestmentStrategy {
  id?: number;
  fundId: number;
  strategyName: string;
  deployedCapital: number;
  currentValue: number;
  allocationPercent: number;
  percentOfTotal?: number;
  irr: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface CashFlow {
  id?: number;
  fundId: number;
  year: number;
  quarter: number;
  quarterLabel: string;
  capitalCalls: number;
  distributions: number;
  netCashFlow: number;
  createdAt?: string;
}

export interface FundActivity {
  id?: number;
  fundId: number;
  activityDate: string;
  description: string;
  amount: number;
  status: 'Completed' | 'In Progress' | 'Scheduled';
  activityType: string;
  createdAt?: string;
}

export interface BenchmarkComparison {
  id?: number;
  fundId: number;
  metricName: string;
  fundValue: number;
  industryBenchmark: number;
  outperformance: number;
  asOfDate: string;
  createdAt?: string;
}

export interface CashFlowSummary {
  totalCapitalCalls: number;
  totalDistributions: number;
  cumulativeNetCash: number;
}

export interface FundOverview {
  fund: Fund;
  metrics: FundMetrics | null;
  quarterlyPerformance: QuarterlyPerformance[];
  strategies: InvestmentStrategy[];
  cashFlows: CashFlow[];
  cashFlowSummary: CashFlowSummary;
  benchmarks: BenchmarkComparison[];
  recentActivities: FundActivity[];
}
