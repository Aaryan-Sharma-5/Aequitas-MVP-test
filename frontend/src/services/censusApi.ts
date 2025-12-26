import type { CensusResponse, AMICalculatorRequest, AMICalculatorResponse } from '../types/census';

const API_BASE_URL = '/api/v1';

export const censusApi = {
  /**
   * Get demographic data for a single ZIP code
   */
  async getDemographics(zipcode: string): Promise<CensusResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/demographics/${zipcode}`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching demographics:', error);
      return {
        success: false,
        error: 'Failed to fetch demographic data',
        code: 'NETWORK_ERROR'
      };
    }
  },

  /**
   * Get demographic data for multiple ZIP codes
   */
  async getDemographicsBatch(zipcodes: string[]): Promise<{
    success: boolean;
    data?: Record<string, any>;
    errors?: Record<string, string>;
    error?: string;
  }> {
    try {
      const response = await fetch(`${API_BASE_URL}/demographics/batch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ zipcodes }),
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching batch demographics:', error);
      return {
        success: false,
        error: 'Failed to fetch demographic data'
      };
    }
  },

  /**
   * Calculate AMI-based rent limits
   */
  async calculateAMI(request: AMICalculatorRequest): Promise<AMICalculatorResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/ami-calculator`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error calculating AMI:', error);
      return {
        success: false,
        error: 'Failed to calculate AMI',
        code: 'NETWORK_ERROR'
      };
    }
  },
};
