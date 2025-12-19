/**
 * TypeScript interfaces for US Census Bureau demographic data
 */

export interface PopulationData {
  totalPopulation: number;
  totalHouseholds: number;
  avgHouseholdSize: number;
}

export interface IncomeData {
  medianHouseholdIncome: number;
  ami30Percent: number;
  ami50Percent: number;
  ami60Percent: number;
  ami80Percent: number;
  incomeDistribution: {
    [bracket: string]: number;
  };
}

export interface HousingData {
  medianHomeValue: number;
  medianGrossRent: number;
  totalHousingUnits: number;
  occupiedUnits: number;
  vacantUnits: number;
  ownerOccupied: number;
  renterOccupied: number;
  occupancyRate: number;
}

export interface DemographicData {
  zipcode: string;
  population: PopulationData;
  income: IncomeData;
  housing: HousingData;
  unemploymentRate: number;
  dataYear: string;
  lastUpdated: string;
}

export interface DemographicsResponse {
  success: boolean;
  data?: DemographicData;
  error?: string;
  code?: string;
  cached?: boolean;
}

export interface AMICalculation {
  zipcode: string;
  amiPercent: number;
  amiIncomeLimit: number;
  maxRent: number;
  areaMedianIncome: number;
  bedrooms: number;
}

export interface AMICalculationResponse {
  success: boolean;
  data?: AMICalculation;
  error?: string;
  code?: string;
}
