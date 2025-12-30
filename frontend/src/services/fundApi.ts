/**
 * API client for fund management operations
 * Communicates with backend REST API for fund data
 */

import type { FundOverview, FundMetrics } from '../types/fund';

const API_BASE_URL = '/api/v1';

class FundApiClient {
  /**
   * Get complete fund overview with all related data
   * This is the primary method used by the FundReturns page
   */
  async getFundOverview(fundId: number): Promise<FundOverview> {
    try {
      const response = await fetch(`${API_BASE_URL}/funds/${fundId}/overview`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch fund overview');
      }

      const data: FundOverview = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching fund overview:', error);
      throw error;
    }
  }

  /**
   * Get latest fund metrics
   */
  async getFundMetrics(fundId: number): Promise<FundMetrics> {
    try {
      const response = await fetch(`${API_BASE_URL}/funds/${fundId}/metrics`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch fund metrics');
      }

      const data = await response.json();
      return data.metrics;
    } catch (error) {
      console.error('Error fetching fund metrics:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const fundApi = new FundApiClient();
