export interface PopulationData {
  total_population: number;
  total_households: number;
  avg_household_size: number;
}

export interface IncomeDistribution {
  under_10k: number;
  '10k_15k': number;
  '15k_20k': number;
  '20k_25k': number;
  '25k_30k': number;
  '30k_35k': number;
  '35k_40k': number;
  '40k_45k': number;
  '45k_50k': number;
  '50k_60k': number;
  '60k_75k': number;
  '75k_100k': number;
  '100k_125k': number;
  '125k_150k': number;
  '150k_200k': number;
  '200k_plus': number;
}

export interface IncomeData {
  median_household_income: number;
  ami_30_percent: number;
  ami_50_percent: number;
  ami_60_percent: number;
  ami_80_percent: number;
  income_distribution: IncomeDistribution;
}

export interface HousingData {
  median_home_value: number;
  median_gross_rent: number;
  total_housing_units: number;
  occupied_units: number;
  vacant_units: number;
  owner_occupied: number;
  renter_occupied: number;
  occupancy_rate: number;
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

export interface CensusResponse {
  success: boolean;
  data?: DemographicData;
  error?: string;
  code?: string;
}

export interface AMICalculatorRequest {
  zipcode: string;
  ami_percent: 30 | 50 | 60 | 80;
  bedrooms: number;
}

export interface AMICalculatorResponse {
  success: boolean;
  data?: {
    zipcode: string;
    ami_percent: number;
    ami_income_limit: number;
    max_rent: number;
    area_median_income: number;
    bedrooms: number;
  };
  error?: string;
  code?: string;
}
