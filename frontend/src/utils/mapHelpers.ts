/**
 * Helper utilities for map functionality
 */

import type { MapProperty, PropertyFilters } from '../types/map';
import type { RentalComparable } from '../types/rentcast';

/**
 * Format a price as a currency string
 * @param price - Price value in dollars
 * @returns Formatted price string (e.g., "$2,500/mo")
 */
export function formatPrice(price: number): string {
  if (!price || price === 0) {
    return 'N/A';
  }

  const formatted = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(price);

  return `${formatted}/mo`;
}

/**
 * Generate a unique ID for a property based on its address
 * @param address - Property address
 * @returns Unique string ID
 */
export function generatePropertyId(address: string): string {
  // Simple hash function for generating IDs from addresses
  let hash = 0;
  for (let i = 0; i < address.length; i++) {
    const char = address.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return `prop-${Math.abs(hash)}-${Date.now()}`;
}

/**
 * Apply filters to a rental comparable
 * @param comparable - RentCast comparable property
 * @param filters - Filter criteria
 * @returns true if property matches filters
 */
export function applyFilters(
  comparable: RentalComparable,
  filters: PropertyFilters
): boolean {
  // Price range filter
  if (filters.priceMin !== undefined && comparable.listedRent !== undefined) {
    if (comparable.listedRent < filters.priceMin) {
      return false;
    }
  }

  if (filters.priceMax !== undefined && comparable.listedRent !== undefined) {
    if (comparable.listedRent > filters.priceMax) {
      return false;
    }
  }

  // Bedrooms filter
  if (filters.bedrooms !== undefined && comparable.bedrooms !== undefined) {
    if (comparable.bedrooms !== filters.bedrooms) {
      return false;
    }
  }

  // Bathrooms filter
  if (filters.bathrooms !== undefined && comparable.bathrooms !== undefined) {
    if (comparable.bathrooms !== filters.bathrooms) {
      return false;
    }
  }

  // Property type filter
  if (filters.propertyType && filters.propertyType !== 'All') {
    if (comparable.propertyType) {
      // Case-insensitive comparison
      const compType = comparable.propertyType.toLowerCase();
      const filterType = filters.propertyType.toLowerCase();
      if (!compType.includes(filterType)) {
        return false;
      }
    }
  }

  return true;
}

/**
 * Calculate the center point of a collection of properties
 * @param properties - Array of map properties
 * @returns [latitude, longitude] center point
 */
export function calculateMapCenter(properties: MapProperty[]): [number, number] {
  if (!properties || properties.length === 0) {
    // Default to Sacramento, CA
    return [38.5816, -121.4944];
  }

  const sum = properties.reduce(
    (acc, prop) => ({
      lat: acc.lat + prop.lat,
      lng: acc.lng + prop.lng
    }),
    { lat: 0, lng: 0 }
  );

  return [
    sum.lat / properties.length,
    sum.lng / properties.length
  ];
}

/**
 * Validate zipcode format
 * @param zipcode - Zipcode string to validate
 * @returns true if valid 5-digit zipcode
 */
export function isValidZipcode(zipcode: string): boolean {
  return /^\d{5}$/.test(zipcode);
}

/**
 * Validate address format
 * @param address - Address string to validate
 * @returns true if non-empty string
 */
export function isValidAddress(address: string): boolean {
  return Boolean(address && address.trim().length > 0);
}

/**
 * Calculate price range statistics from properties
 * @param properties - Array of map properties
 * @returns Object with min, max, and average prices
 */
export function calculatePriceStats(properties: MapProperty[]): {
  min: number;
  max: number;
  average: number;
} {
  if (!properties || properties.length === 0) {
    return { min: 0, max: 0, average: 0 };
  }

  const prices = properties.map(p => p.price).filter(p => p > 0);

  if (prices.length === 0) {
    return { min: 0, max: 0, average: 0 };
  }

  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const average = prices.reduce((sum, price) => sum + price, 0) / prices.length;

  return { min, max, average };
}

/**
 * Determine marker color based on price relative to average
 * @param price - Property price
 * @param averagePrice - Average price in the dataset
 * @returns Color name for marker ('green' | 'yellow' | 'red')
 */
export function getMarkerColor(price: number, averagePrice: number): 'green' | 'yellow' | 'red' {
  if (averagePrice === 0) {
    return 'red'; // Default color when no average available
  }

  if (price < averagePrice * 0.9) {
    return 'green'; // Below market
  } else if (price > averagePrice * 1.1) {
    return 'red'; // Above market
  } else {
    return 'yellow'; // Market average
  }
}
