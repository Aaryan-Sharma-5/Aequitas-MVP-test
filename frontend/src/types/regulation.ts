export type RegulationStatus = 'compliant' | 'concerning' | 'negotiation' | 'active' | 'proposed' | 'needed';

export interface Regulation {
  id: string;
  title: string;
  description: string;
  status: RegulationStatus;
  effectiveDate: string;
  sunset?: string;
}

export interface RegulatoryChange {
  id: string;
  title: string;
  description: string;
  status: 'proposed' | 'enacted';
  proposedDate?: string;
  enactedDate?: string;
  effectiveDate?: string;
}

export interface Market {
  id: string;
  name: string;
  state: string;
  riskScore: number;
}

export interface MarketRegulationsSummary {
  market: Market;
  lastChecked: string;
  compliantCount: number;
  concerningCount: number;
  proposedChangesCount: number;
  currentRegulations: Regulation[];
  upcomingChanges: RegulatoryChange[];
}
