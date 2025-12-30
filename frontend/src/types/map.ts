/**
 * Type definitions for map-related components and data structures
 */

export interface MapProperty {
  id: string;
  address: string;
  lat: number;
  lng: number;
  price: number;
  priceFormatted: string;
  bedrooms?: number;
  bathrooms?: number;
  squareFootage?: number;
  propertyType?: string;
  daysOnMarket?: number;
  distanceMiles?: number;
  listingUrl?: string;
}

export interface SearchParams {
  searchType: 'zipcode' | 'address';
  searchValue: string;
}

export interface PropertyFilters {
  priceMin?: number;
  priceMax?: number;
  bedrooms?: number;
  bathrooms?: number;
  propertyType?: 'Rental' | 'Sale' | 'All';
}

export interface GeocodingResult {
  lat: number;
  lng: number;
  displayName: string;
}
