/**
 * RentCast API client for rental market intelligence
 */

import type {
  RentEstimateData,
  MarketStatistics,
  PropertyValuation,
  RentCastResponse,
  RentCastComparablesResponse,
  RentCastTrendsResponse,
} from '../types/rentcast';

const API_BASE_URL = '/api/v1';

/**
 * Parameters for rent estimate request
 */
export interface RentEstimateParams {
  address?: string;
  zipcode?: string;
  bedrooms?: number;
  bathrooms?: number;
  squareFootage?: number;
}

/**
 * Parameters for rental comparables request
 */
export interface RentalComparablesParams extends RentEstimateParams {
  compCount?: number;
  maxRadius?: number;
}

/**
 * RentCast API service
 */
export const rentcastApi = {
  /**
   * Get rent estimate for a property
   */
  async getRentEstimate(
    params: RentEstimateParams
  ): Promise<RentCastResponse<RentEstimateData>> {
    try {
      const queryParams = new URLSearchParams();

      if (params.address) queryParams.append('address', params.address);
      if (params.zipcode) queryParams.append('zipcode', params.zipcode);
      if (params.bedrooms !== undefined)
        queryParams.append('bedrooms', params.bedrooms.toString());
      if (params.bathrooms !== undefined)
        queryParams.append('bathrooms', params.bathrooms.toString());
      if (params.squareFootage !== undefined)
        queryParams.append('squareFootage', params.squareFootage.toString());

      const response = await fetch(
        `${API_BASE_URL}/rentcast/rent-estimate?${queryParams}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to fetch rent estimate',
          code: errorData.code,
        };
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        code: 'NETWORK_ERROR',
      };
    }
  },

  /**
   * Get rental comparable properties
   */
  async getComparables(
    params: RentalComparablesParams
  ): Promise<RentCastComparablesResponse> {
    try {
      const queryParams = new URLSearchParams();

      if (params.address) queryParams.append('address', params.address);
      if (params.zipcode) queryParams.append('zipcode', params.zipcode);
      if (params.bedrooms !== undefined)
        queryParams.append('bedrooms', params.bedrooms.toString());
      if (params.bathrooms !== undefined)
        queryParams.append('bathrooms', params.bathrooms.toString());
      if (params.compCount !== undefined)
        queryParams.append('compCount', params.compCount.toString());
      if (params.maxRadius !== undefined)
        queryParams.append('maxRadius', params.maxRadius.toString());

      const response = await fetch(
        `${API_BASE_URL}/rentcast/comparables?${queryParams}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to fetch rental comparables',
          code: errorData.code,
        };
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        code: 'NETWORK_ERROR',
      };
    }
  },

  /**
   * Get market statistics for a ZIP code
   */
  async getMarketStats(
    zipcode: string,
    dataType: 'Rental' | 'Sale' | 'All' = 'Rental'
  ): Promise<RentCastResponse<MarketStatistics>> {
    try {
      const queryParams = new URLSearchParams({
        zipcode,
        dataType,
      });

      const response = await fetch(
        `${API_BASE_URL}/rentcast/market-stats?${queryParams}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to fetch market statistics',
          code: errorData.code,
        };
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        code: 'NETWORK_ERROR',
      };
    }
  },

  /**
   * Get historical market trends for a ZIP code
   */
  async getMarketTrends(
    zipcode: string,
    months: number = 12,
    dataType: 'Rental' | 'Sale' | 'All' = 'Rental'
  ): Promise<RentCastTrendsResponse> {
    try {
      const queryParams = new URLSearchParams({
        zipcode,
        months: months.toString(),
        dataType,
      });

      const response = await fetch(
        `${API_BASE_URL}/rentcast/market-trends?${queryParams}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to fetch market trends',
          code: errorData.code,
        };
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        code: 'NETWORK_ERROR',
      };
    }
  },

  /**
   * Get complete property valuation (estimate + comparables + market stats)
   */
  async getPropertyValuation(
    params: RentEstimateParams
  ): Promise<RentCastResponse<PropertyValuation>> {
    try {
      const queryParams = new URLSearchParams();

      if (params.address) queryParams.append('address', params.address);
      if (params.zipcode) queryParams.append('zipcode', params.zipcode);
      if (params.bedrooms !== undefined)
        queryParams.append('bedrooms', params.bedrooms.toString());
      if (params.bathrooms !== undefined)
        queryParams.append('bathrooms', params.bathrooms.toString());
      if (params.squareFootage !== undefined)
        queryParams.append('squareFootage', params.squareFootage.toString());

      const response = await fetch(
        `${API_BASE_URL}/rentcast/property-valuation?${queryParams}`
      );

      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Failed to fetch property valuation',
          code: errorData.code,
        };
      }

      const data = await response.json();
      return data;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Network error',
        code: 'NETWORK_ERROR',
      };
    }
  },
};
