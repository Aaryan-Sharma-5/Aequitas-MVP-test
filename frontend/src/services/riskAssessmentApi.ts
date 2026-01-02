/**
 * API Service for Risk Assessment System
 * Handles all communication with the risk assessment backend endpoints
 */

import {
  RiskAssessment,
  DealMemo,
  BenchmarkData,
  MarketThresholds,
  DealComparison,
  RiskAssessmentResponse,
  DealMemoResponse,
  BenchmarkDataResponse,
  MarketThresholdsResponse,
  DealComparisonResponse,
} from '../types/riskAssessment';

const API_BASE_URL = '/api/v1';

/**
 * Calculate comprehensive risk assessment for a deal
 */
export const calculateRiskAssessment = async (
  dealId: number,
  holdingPeriod: number = 10,
  geography: string = 'US'
): Promise<RiskAssessment> => {
  const response = await fetch(
    `${API_BASE_URL}/deals/${dealId}/risk-assessment?holding_period=${holdingPeriod}&geography=${geography}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to calculate risk assessment');
  }

  const data: RiskAssessmentResponse = await response.json();
  if (!data.success || !data.data) {
    throw new Error(data.error || 'Failed to calculate risk assessment');
  }

  return data.data;
};

/**
 * Get existing risk assessment for a deal
 */
export const getRiskAssessment = async (dealId: number): Promise<RiskAssessment | null> => {
  const response = await fetch(`${API_BASE_URL}/deals/${dealId}/risk-assessment`);

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch risk assessment');
  }

  const data: RiskAssessmentResponse = await response.json();
  if (!data.success) {
    throw new Error(data.error || 'Failed to fetch risk assessment');
  }

  return data.data || null;
};

/**
 * Generate comprehensive deal memo
 */
export const getDealMemo = async (
  dealId: number,
  holdingPeriod: number = 10,
  geography: string = 'US'
): Promise<DealMemo> => {
  const response = await fetch(
    `${API_BASE_URL}/deals/${dealId}/deal-memo?holding_period=${holdingPeriod}&geography=${geography}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to generate deal memo');
  }

  const data: DealMemoResponse = await response.json();
  if (!data.success || !data.data) {
    throw new Error(data.error || 'Failed to generate deal memo');
  }

  return data.data;
};

/**
 * Compare multiple deals side-by-side
 */
export const compareDeals = async (
  dealIds: number[],
  holdingPeriod: number = 10
): Promise<DealComparison> => {
  const response = await fetch(`${API_BASE_URL}/deals/compare`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      deal_ids: dealIds,
      holding_period: holdingPeriod,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to compare deals');
  }

  const data: DealComparisonResponse = await response.json();
  if (!data.success || !data.data) {
    throw new Error(data.error || 'Failed to compare deals');
  }

  return data.data;
};

/**
 * Get benchmark data for a specific rent decile
 */
export const getBenchmarkData = async (
  decile: number,
  geography: string = 'US'
): Promise<BenchmarkData> => {
  const response = await fetch(
    `${API_BASE_URL}/benchmarks/decile/${decile}?geography=${geography}`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch benchmark data');
  }

  const data: BenchmarkDataResponse = await response.json();
  if (!data.success || !data.data) {
    throw new Error(data.error || 'Failed to fetch benchmark data');
  }

  return data.data;
};

/**
 * Get market rent decile thresholds
 */
export const getMarketThresholds = async (
  geography: string = 'national',
  bedrooms?: number
): Promise<MarketThresholds> => {
  const params = new URLSearchParams({ geography });
  if (bedrooms !== undefined) {
    params.append('bedrooms', bedrooms.toString());
  }

  const response = await fetch(`${API_BASE_URL}/market-thresholds?${params.toString()}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch market thresholds');
  }

  const data: MarketThresholdsResponse = await response.json();
  if (!data.success || !data.data) {
    throw new Error(data.error || 'Failed to fetch market thresholds');
  }

  return data.data;
};

/**
 * Get deal with its risk assessment in single response
 */
export const getDealWithAssessment = async (dealId: number): Promise<{
  deal: any;
  riskAssessment: RiskAssessment | null;
}> => {
  const response = await fetch(`${API_BASE_URL}/deals/${dealId}/summary`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to fetch deal summary');
  }

  const data = await response.json();
  if (!data.success || !data.data) {
    throw new Error(data.error || 'Failed to fetch deal summary');
  }

  return data.data;
};

/**
 * Convert snake_case API response to camelCase for TypeScript
 */
export const convertToCamelCase = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map((item) => convertToCamelCase(item));
  } else if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = key.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
      result[camelKey] = convertToCamelCase(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
};

export default {
  calculateRiskAssessment,
  getRiskAssessment,
  getDealMemo,
  compareDeals,
  getBenchmarkData,
  getMarketThresholds,
  getDealWithAssessment,
};
