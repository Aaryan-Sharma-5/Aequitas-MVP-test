/**
 * RentCast API TypeScript types for rental market intelligence
 */

export interface RentEstimateData {
  address: string;
  zipcode: string;
  bedrooms?: number;
  bathrooms?: number;
  squareFootage?: number;
  estimatedRent?: number;
  rentRangeLow?: number;
  rentRangeHigh?: number;
  pricePerSqft?: number;
  propertyType?: string;
  lastUpdated?: string;
}

export interface RentalComparable {
  address: string;
  distanceMiles: number;
  bedrooms?: number;
  bathrooms?: number;
  squareFootage?: number;
  listedRent?: number;
  pricePerSqft?: number;
  propertyType?: string;
  daysOnMarket?: number;
  listingUrl?: string;
}

export interface MarketStatistics {
  zipcode: string;
  dataMonth: string;
  avgRentAll?: number;
  medianRentAll?: number;
  avgRent1bed?: number;
  avgRent2bed?: number;
  avgRent3bed?: number;
  avgRent4bed?: number;
  totalListings?: number;
  avgDaysOnMarket?: number;
  inventoryLevel?: 'Low' | 'Medium' | 'High';
  lastUpdated?: string;
}

export interface MarketTrend {
  date: string;
  avgRent?: number;
  medianRent?: number;
  listingCount?: number;
}

export interface PropertyValuation {
  rentEstimate: RentEstimateData;
  comparables: RentalComparable[];
  marketStats?: MarketStatistics;
  lastUpdated?: string;
}

// API Response types
export interface RentCastResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  code?: string;
  lastUpdated?: string;
}

export interface RentCastComparablesResponse extends RentCastResponse<RentalComparable[]> {
  count?: number;
}

export interface RentCastTrendsResponse extends RentCastResponse<MarketTrend[]> {
  months?: number;
}
