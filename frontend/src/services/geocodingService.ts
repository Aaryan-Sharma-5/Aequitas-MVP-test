/**
 * Geocoding service using Nominatim (OpenStreetMap) API
 * Provides address to lat/lng conversion with caching and rate limiting
 */

import type { GeocodingResult } from '../types/map';

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org/search';
const RATE_LIMIT_DELAY = 1000; // 1 second between requests
const CACHE_EXPIRY = 24 * 60 * 60 * 1000; // 24 hours

interface CachedResult {
  result: GeocodingResult;
  timestamp: number;
}

class GeocodingService {
  private cache: Map<string, CachedResult> = new Map();
  private requestQueue: Array<() => Promise<void>> = [];
  private isProcessing = false;
  private lastRequestTime = 0;

  /**
   * Process the request queue with rate limiting
   */
  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.requestQueue.length === 0) {
      return;
    }

    this.isProcessing = true;

    while (this.requestQueue.length > 0) {
      const now = Date.now();
      const timeSinceLastRequest = now - this.lastRequestTime;

      if (timeSinceLastRequest < RATE_LIMIT_DELAY) {
        await new Promise(resolve =>
          setTimeout(resolve, RATE_LIMIT_DELAY - timeSinceLastRequest)
        );
      }

      const request = this.requestQueue.shift();
      if (request) {
        await request();
        this.lastRequestTime = Date.now();
      }
    }

    this.isProcessing = false;
  }

  /**
   * Add a request to the queue
   */
  private queueRequest<T>(request: () => Promise<T>): Promise<T> {
    return new Promise((resolve, reject) => {
      this.requestQueue.push(async () => {
        try {
          const result = await request();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
      this.processQueue();
    });
  }

  /**
   * Get cached result if available and not expired
   */
  private getCached(key: string): GeocodingResult | null {
    const cached = this.cache.get(key);
    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > CACHE_EXPIRY) {
      this.cache.delete(key);
      return null;
    }

    return cached.result;
  }

  /**
   * Store result in cache
   */
  private setCached(key: string, result: GeocodingResult): void {
    this.cache.set(key, {
      result,
      timestamp: Date.now()
    });
  }

  /**
   * Make a geocoding request to Nominatim
   */
  private async makeRequest(query: string): Promise<GeocodingResult | null> {
    try {
      const params = new URLSearchParams({
        q: query,
        format: 'json',
        limit: '1',
        addressdetails: '1'
      });

      const response = await fetch(`${NOMINATIM_BASE_URL}?${params}`, {
        headers: {
          'User-Agent': 'Aequitas-MVP/1.0' // Required by Nominatim
        }
      });

      if (!response.ok) {
        console.error('Geocoding request failed:', response.statusText);
        return null;
      }

      const data = await response.json();

      if (!data || data.length === 0) {
        return null;
      }

      const result = data[0];
      return {
        lat: parseFloat(result.lat),
        lng: parseFloat(result.lon),
        displayName: result.display_name
      };
    } catch (error) {
      console.error('Geocoding error:', error);
      return null;
    }
  }

  /**
   * Geocode a full address
   */
  async geocodeAddress(address: string): Promise<GeocodingResult | null> {
    if (!address || address.trim().length === 0) {
      return null;
    }

    const cacheKey = `address:${address.toLowerCase()}`;
    const cached = this.getCached(cacheKey);
    if (cached) {
      return cached;
    }

    const result = await this.queueRequest(() => this.makeRequest(address));

    if (result) {
      this.setCached(cacheKey, result);
    }

    return result;
  }

  /**
   * Geocode a zipcode
   */
  async geocodeZipcode(zipcode: string): Promise<GeocodingResult | null> {
    if (!zipcode || !/^\d{5}$/.test(zipcode)) {
      return null;
    }

    const cacheKey = `zipcode:${zipcode}`;
    const cached = this.getCached(cacheKey);
    if (cached) {
      return cached;
    }

    // Add USA to the query for better results
    const query = `${zipcode}, USA`;
    const result = await this.queueRequest(() => this.makeRequest(query));

    if (result) {
      this.setCached(cacheKey, result);
    }

    return result;
  }

  /**
   * Reverse geocode coordinates to get an address
   */
  async reverseGeocode(lat: number, lng: number): Promise<string | null> {
    if (!lat || !lng) {
      return null;
    }

    const cacheKey = `reverse:${lat.toFixed(6)}:${lng.toFixed(6)}`;
    const cached = this.getCached(cacheKey);
    if (cached) {
      return cached.displayName;
    }

    try {
      const params = new URLSearchParams({
        lat: lat.toString(),
        lon: lng.toString(),
        format: 'json',
        addressdetails: '1'
      });

      const response = await this.queueRequest(() =>
        fetch(`https://nominatim.openstreetmap.org/reverse?${params}`, {
          headers: {
            'User-Agent': 'Aequitas-MVP/1.0'
          }
        }).then(res => {
          if (!res.ok) {
            throw new Error('Reverse geocoding failed');
          }
          return res.json();
        })
      );

      if (!response || response.error) {
        return null;
      }

      const address = response.display_name;

      // Cache the result
      const geocodingResult: GeocodingResult = {
        lat,
        lng,
        displayName: address
      };
      this.setCached(cacheKey, geocodingResult);

      return address;

    } catch (error) {
      console.error('Reverse geocoding error:', error);
      return null;
    }
  }

  /**
   * Batch geocode multiple addresses
   * Returns a map of address -> coordinates
   */
  async batchGeocode(addresses: string[]): Promise<Map<string, GeocodingResult>> {
    const results = new Map<string, GeocodingResult>();

    // Filter out duplicates and empty addresses
    const uniqueAddresses = [...new Set(addresses.filter(addr => addr && addr.trim()))];

    // Process each address
    const promises = uniqueAddresses.map(async (address) => {
      const result = await this.geocodeAddress(address);
      if (result) {
        results.set(address, result);
      }
    });

    await Promise.all(promises);

    return results;
  }

  /**
   * Batch reverse geocode multiple coordinate pairs
   * Returns a map of "lat,lng" -> address
   */
  async batchReverseGeocode(coordinates: Array<{ lat: number; lng: number }>): Promise<Map<string, string>> {
    const results = new Map<string, string>();

    // Process each coordinate pair
    const promises = coordinates.map(async (coord) => {
      const address = await this.reverseGeocode(coord.lat, coord.lng);
      if (address) {
        const key = `${coord.lat},${coord.lng}`;
        results.set(key, address);
      }
    });

    await Promise.all(promises);

    return results;
  }

  /**
   * Clear the cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache size
   */
  getCacheSize(): number {
    return this.cache.size;
  }
}

// Export a singleton instance
export const geocodingService = new GeocodingService();
