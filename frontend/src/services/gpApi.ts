/**
 * API client for GP (General Partner) management operations
 * Communicates with backend REST API for GP data
 */

import type { GP, GPOverview, GPPerformanceComparison, GPTopPerformers } from '../types/gp';

const API_BASE_URL = '/api/v1';

class GPApiClient {
  /**
   * Get all GPs
   */
  async getAllGPs(): Promise<GP[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch GPs');
      }

      const data = await response.json();
      return data.gps;
    } catch (error) {
      console.error('Error fetching GPs:', error);
      throw error;
    }
  }

  /**
   * Get a single GP by ID
   */
  async getGP(gpId: number): Promise<GP> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps/${gpId}`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch GP');
      }

      const data = await response.json();
      return data.gp;
    } catch (error) {
      console.error('Error fetching GP:', error);
      throw error;
    }
  }

  /**
   * Get complete GP overview with all related data
   * This is the primary method used by the GP Portfolio page
   */
  async getGPOverview(gpId: number): Promise<GPOverview> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps/${gpId}/overview`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch GP overview');
      }

      const data: GPOverview = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching GP overview:', error);
      throw error;
    }
  }

  /**
   * Get performance comparison data for all GPs
   */
  async getPerformanceComparison(): Promise<GPPerformanceComparison[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps/performance-comparison`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch performance comparison');
      }

      const data = await response.json();
      return data.comparison;
    } catch (error) {
      console.error('Error fetching performance comparison:', error);
      throw error;
    }
  }

  /**
   * Get top performing GPs and those needing attention
   */
  async getTopPerformers(): Promise<GPTopPerformers> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps/top-performers`);

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch top performers');
      }

      const data: GPTopPerformers = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching top performers:', error);
      throw error;
    }
  }

  /**
   * Create a new GP
   */
  async createGP(gpData: Partial<GP>): Promise<GP> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gpData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to create GP');
      }

      const data = await response.json();
      return data.gp;
    } catch (error) {
      console.error('Error creating GP:', error);
      throw error;
    }
  }

  /**
   * Update an existing GP
   */
  async updateGP(gpId: number, gpData: Partial<GP>): Promise<GP> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps/${gpId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(gpData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to update GP');
      }

      const data = await response.json();
      return data.gp;
    } catch (error) {
      console.error('Error updating GP:', error);
      throw error;
    }
  }

  /**
   * Delete a GP
   */
  async deleteGP(gpId: number): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/gps/${gpId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to delete GP');
      }
    } catch (error) {
      console.error('Error deleting GP:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const gpApi = new GPApiClient();
