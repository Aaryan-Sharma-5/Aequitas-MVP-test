/**
 * TypeScript type definitions for GP (General Partner) related data structures
 */

export interface GP {
  id?: number;
  gpName: string;
  location?: string;
  tier?: string;
  performanceRating?: string;
  createdAt?: string;
  updatedAt?: string;
  contactEmail?: string;
  contactPhone?: string;
  website?: string;
  netIrr?: number;
  grossIrr?: number;
  irrTrend?: number;
  totalAum?: number;
  dealCount?: number;
  currentValue?: number;
  tags?: string;
}

export interface GPQuarterlyPerformance {
  id?: number;
  gpId: number;
  year: number;
  quarter: number;
  quarterLabel?: string;
  irr?: number;
  createdAt?: string;
}

export interface GPPortfolioSummary {
  id?: number;
  gpId: number;
  year: number;
  quartile: number;
  dealCount?: number;
  percentage?: number;
  createdAt?: string;
}

export interface GPOverview {
  gp: GP;
  quarterlyPerformance: GPQuarterlyPerformance[];
  portfolioSummary: GPPortfolioSummary[];
}

export interface GPPerformanceComparison {
  gpName: string;
  netIrr?: number;
  gpId: number;
}

export interface GPTopPerformers {
  topPerformer?: {
    gpName: string;
    netIrr?: number;
    performanceRating?: string;
  };
  needsAttention: Array<{
    gpName: string;
    netIrr?: number;
    irrTrend?: number;
    reason: string;
  }>;
}
