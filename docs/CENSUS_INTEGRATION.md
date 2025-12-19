# Census API Integration - Implementation Summary

## Overview

This document describes the complete US Census Bureau API integration implemented for the Aequitas affordable housing platform. The integration provides comprehensive demographic and economic data at the ZIP code level to enhance property analysis, market insights, and underwriting calculations.

## Features Implemented

### 1. Backend (Python/Flask)

#### Census Service Layer
**File**: `backend/app/services/census_service.py`

- Full integration with Census Bureau ACS 5-Year Estimates API
- Fetches 20+ demographic variables including:
  - **Population**: Total population, households, household size
  - **Income**: Median income, income distribution across 16 brackets, AMI calculations (30%, 50%, 60%, 80%)
  - **Housing**: Median home value, median rent, occupancy rates, tenure data
  - **Employment**: Unemployment rate, labor force statistics
- In-memory caching with 24-hour TTL to minimize API calls
- Comprehensive error handling for invalid ZIPs, rate limits, and network failures
- AMI rent limit calculator

#### Data Models
**File**: `backend/app/models/census_models.py`

- `PopulationData`: Population and household statistics
- `IncomeData`: Income statistics and AMI calculations
- `HousingData`: Housing market characteristics
- `DemographicData`: Complete demographic profile with JSON serialization

#### API Endpoints
**File**: `backend/app/api/v1/routes.py`

1. **GET `/api/v1/demographics/<zipcode>`**
   - Returns comprehensive demographic data for a single ZIP code
   - Example: `GET /api/v1/demographics/95814`

2. **POST `/api/v1/demographics/batch`**
   - Fetch demographics for multiple ZIP codes in one request
   - Maximum 50 ZIP codes per request
   - Example payload: `{"zipcodes": ["95814", "95819", "95818"]}`

3. **POST `/api/v1/ami-calculator`**
   - Calculate AMI-based rent limits for a property
   - Example payload: `{"zipcode": "95814", "ami_percent": 60, "bedrooms": 2}`

4. **Enhanced GET `/api/v1/metrics`**
   - Original metrics plus new market insights:
     - Average AMI served across portfolio
     - Total markets
     - Average market income
     - Average occupancy rate
     - Average median rent

#### Configuration
**Files**: `backend/config.py`, `backend/.env`, `backend/.env.example`

- `CENSUS_API_KEY`: Your Census API key (optional but recommended)
- `CENSUS_API_BASE_URL`: Census API base URL (default: https://api.census.gov/data)
- `CENSUS_API_YEAR`: ACS dataset year (default: 2022)
- `CENSUS_CACHE_TTL`: Cache time-to-live in seconds (default: 86400)

### 2. Frontend (React/TypeScript)

#### Type Definitions
**File**: `frontend/src/types/census.ts`

TypeScript interfaces for all Census data types:
- `PopulationData`, `IncomeData`, `HousingData`, `DemographicData`
- `DemographicsResponse`, `AMICalculation`, `AMICalculationResponse`

#### Dashboard Enhancements
**File**: `frontend/src/pages/Dashboard.tsx`

- New "Market Insights" section with 4 gradient cards:
  - Average AMI Served (%)
  - Markets Served (count)
  - Average Market Income ($)
  - Average Median Rent ($)
- Fetches enhanced metrics from backend
- Responsive grid layout

#### Property Map Integration
**File**: `frontend/src/components/PropertyMap.tsx`

- ZIP codes automatically extracted from property addresses
- Demographics fetched when popup is opened
- Enhanced popups display:
  - Median household income
  - 60% AMI threshold
  - Median rent
  - Total households
  - Occupancy rate
- Loading states and error handling
- Client-side caching of fetched demographics

#### Underwriting Auto-Population
**File**: `frontend/src/pages/Underwriting.tsx`

- New ZIP code input field with "Fetch Data" button
- Auto-populates:
  - Average Monthly Rent (from median gross rent)
  - AMI dropdown values (calculated from median income)
- Market Context panel displays:
  - Median income
  - Median rent
  - Occupancy rate
  - Total households
- Dynamic AMI options showing actual dollar amounts
- Loading states and error messages

#### Market Analysis Page (NEW)
**File**: `frontend/src/pages/MarketAnalysis.tsx`

Complete demographic analysis dashboard with:

**Search Section**:
- ZIP code input with instant analysis

**Overview Cards**:
- Total Population
- Total Households
- Median Income
- Occupancy Rate

**AMI Thresholds Section**:
- Display all four AMI levels (30%, 50%, 60%, 80%) with dollar amounts

**Visualizations**:
- **Household Income Distribution** (Bar Chart)
  - Income brackets from <$25k to $200k+
  - Shows household counts in each bracket
- **Housing Tenure** (Pie Chart)
  - Owner-occupied vs Renter-occupied units
  - Shows percentages and absolute numbers

**Housing Market Metrics**:
- Median home value
- Median gross rent
- Total housing units
- Vacancy rate
- Unemployment rate

**Affordability Analysis**:
- 60% AMI max affordable rent calculation (30% of monthly income)
- Market median rent comparison
- Affordability gap percentage
- Visual indicator (red if unaffordable, green if affordable)

**Data Source Attribution**:
- Displays ACS dataset year and last updated timestamp

#### Navigation
**Files**: `frontend/src/App.tsx`, `frontend/src/components/Sidebar.tsx`

- Added "Market Analysis" to navigation menu with BarChart3 icon
- Route: `/market-analysis`

### 3. Documentation

**File**: `docs/CENSUS_API_SETUP.md`

Step-by-step guide including:
- How to obtain a Census API key
- Configuration instructions
- API rate limits (500/day without key, unlimited with key)
- Troubleshooting tips
- Additional resources and links

## Installation & Setup

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your CENSUS_API_KEY
   ```

3. **Get Census API Key**:
   - Visit https://api.census.gov/data/key_signup.html
   - Fill out the form
   - Check your email for the API key
   - Add to `.env` file

4. **Start Backend**:
   ```bash
   python run.py
   ```

### Frontend Setup

No additional setup required - TypeScript types are automatically available.

## Testing the Integration

### 1. Test Census API Endpoint

```bash
# Test demographics endpoint
curl http://localhost:5000/api/v1/demographics/95814

# Expected response:
{
  "success": true,
  "data": {
    "zipcode": "95814",
    "population": { ... },
    "income": { ... },
    "housing": { ... },
    "unemploymentRate": 4.2,
    "dataYear": "2018-2022",
    "lastUpdated": "2025-12-19T..."
  }
}
```

### 2. Test AMI Calculator

```bash
curl -X POST http://localhost:5000/api/v1/ami-calculator \
  -H "Content-Type: application/json" \
  -d '{"zipcode": "95814", "ami_percent": 60, "bedrooms": 2}'

# Expected response:
{
  "success": true,
  "data": {
    "zipcode": "95814",
    "amiPercent": 60,
    "amiIncomeLimit": 48000,
    "maxRent": 1200,
    "areaMedianIncome": 80000,
    "bedrooms": 2
  }
}
```

### 3. Test Frontend Features

1. **Dashboard**: Visit http://localhost:5173 and verify Market Insights section appears
2. **Property Map**: Click on any property marker and verify demographics load in popup
3. **Underwriting**: Enter ZIP code "95814" and click "Fetch Data" - verify Market Context panel appears
4. **Market Analysis**: Navigate to Market Analysis page and analyze ZIP 95814

## Census Variables Used

### Population Variables
- `B01003_001E`: Total Population
- `B11001_001E`: Total Households
- `B25010_001E`: Average Household Size

### Income Variables
- `B19013_001E`: Median Household Income
- `B19001_002E` through `B19001_017E`: Income Distribution (16 brackets)

### Housing Variables
- `B25077_001E`: Median Home Value
- `B25064_001E`: Median Gross Rent
- `B25001_001E`: Total Housing Units
- `B25002_002E`: Occupied Housing Units
- `B25002_003E`: Vacant Housing Units
- `B25003_002E`: Owner-Occupied Units
- `B25003_003E`: Renter-Occupied Units

### Employment Variables
- `B23025_005E`: Unemployment Count
- `B23025_003E`: Labor Force

## Architecture Decisions

### 1. Data Source: ACS 5-Year Estimates
- Most reliable and comprehensive data
- Covers all geographic areas
- Updated annually with 5-year rolling averages
- Default year: 2022 (representing 2018-2022 data)

### 2. Caching Strategy
- In-memory cache with 24-hour TTL
- Simple implementation, no external dependencies
- Cache key pattern: `census:{zipcode}:{api_year}`
- LRU eviction when cache reaches 1000 entries

### 3. Error Handling
- Graceful degradation - shows properties even if demographics fail
- User-friendly error messages
- Fallback to default values when appropriate
- Comprehensive logging for debugging

### 4. Performance Optimizations
- Lazy loading - demographics fetched only when needed (popup open)
- Client-side caching to prevent duplicate requests
- Batch endpoint for efficient multi-ZIP fetching
- Memoized calculations in React components

## API Rate Limits

- **Without API Key**: 500 requests per IP per day
- **With API Key**: Unlimited (fair use policy)

For production use, obtaining an API key is essential.

## Future Enhancements

Potential improvements for future development:

1. **Redis Cache**: Replace in-memory cache with Redis for multi-server deployments
2. **Historical Trends**: Compare data across multiple ACS years
3. **Additional Geography Levels**: Support for counties, MSAs, census tracts
4. **Advanced Analytics**: Predictive modeling, market scoring algorithms
5. **Export Functionality**: Generate PDF/Excel reports with demographic data
6. **WebSocket Updates**: Real-time demographic data updates
7. **Custom Market Reports**: Formatted reports with charts and analysis
8. **Geocoding Service**: Automatically extract ZIP from street addresses

## Troubleshooting

### Issue: "Invalid API Key" Error
**Solution**: Verify the API key is correctly set in `.env` file with no extra spaces

### Issue: "No Data for ZIP Code"
**Solution**: Some ZIPs may not have ACS data. Try a well-populated ZIP (e.g., 10001, 90210)

### Issue: "Rate Limit Exceeded"
**Solution**: Register for a free API key at https://api.census.gov/data/key_signup.html

### Issue: Demographics not loading on map
**Solution**: Check browser console for errors. Ensure backend is running and accessible.

## Files Modified/Created

### Backend Files
**Created**:
- `backend/app/services/__init__.py`
- `backend/app/services/census_service.py` (379 lines)
- `backend/app/models/__init__.py`
- `backend/app/models/census_models.py` (64 lines)
- `backend/.env.example`
- `backend/.env`
- `docs/CENSUS_API_SETUP.md`

**Modified**:
- `backend/config.py` - Added Census configuration
- `backend/requirements.txt` - Added requests, cachetools, python-dateutil
- `backend/app/api/v1/routes.py` - Added 3 new endpoints, enhanced metrics

### Frontend Files
**Created**:
- `frontend/src/types/census.ts` (62 lines)
- `frontend/src/pages/MarketAnalysis.tsx` (453 lines)

**Modified**:
- `frontend/src/components/PropertyMap.tsx` - Added demographics fetching and display
- `frontend/src/pages/Dashboard.tsx` - Added Market Insights section
- `frontend/src/pages/Underwriting.tsx` - Added ZIP field, fetch button, market context
- `frontend/src/App.tsx` - Added MarketAnalysis route
- `frontend/src/components/Sidebar.tsx` - Added Market Analysis nav item

## Resources

- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [ACS 5-Year Data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [Variable Search Tool](https://api.census.gov/data/2022/acs/acs5/variables.html)
- [Census Reporter](https://censusreporter.org/) - Visual data exploration

## Support

For issues or questions:
- Census API Support: census.api@census.gov
- Aequitas Platform: Contact your development team

---

**Implementation Date**: December 2025
**Census Dataset**: 2022 ACS 5-Year Estimates (2018-2022)
**Integration Version**: 1.0
