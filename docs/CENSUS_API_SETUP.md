# US Census API Setup Guide

## Obtaining a Census API Key

The US Census Bureau provides free API access to demographic and economic data. While the API can be used without a key (with limited requests), we strongly recommend obtaining a free API key for unlimited access.

### Step-by-Step Instructions

1. **Visit the Census API Key Request Page**

   Navigate to: [https://api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)

2. **Fill Out the Registration Form**

   Provide the following information:
   - **Organization Name**: Aequitas Housing (or your organization)
   - **Email Address**: Your valid email address
   - **Intended Usage**: Affordable Housing Market Analysis and Demographic Research

3. **Submit the Form**

   Click the "Submit" button to send your request.

4. **Check Your Email**

   You should receive an email with your API key within a few minutes. The subject line will be "Your U.S. Census Bureau API Key".

5. **Copy Your API Key**

   The email will contain your unique API key - a long alphanumeric string (example: `abc123def456...`).

6. **Add to Your Environment Configuration**

   Create a `.env` file in the `backend` directory (if it doesn't exist):

   ```bash
   cd backend
   cp .env.example .env
   ```

   Edit the `.env` file and add your API key:

   ```bash
   CENSUS_API_KEY=your_actual_api_key_here
   ```

7. **Verify the Setup**

   Restart your Flask backend server and test the Census API integration:

   ```bash
   python run.py
   ```

   Then test the demographics endpoint:

   ```bash
   curl "http://localhost:5000/api/v1/demographics/95814"
   ```

   You should receive demographic data for Sacramento, CA (ZIP 95814).

## API Rate Limits

- **Without API Key**: 500 requests per IP address per day
- **With API Key**: Unlimited requests (subject to fair use policy)

For production use, an API key is essential to avoid rate limiting.

## Data Sources

This integration uses the **American Community Survey (ACS) 5-Year Estimates**, which provides:
- Most reliable and comprehensive demographic data
- Covers all geographic areas (even small populations)
- Updated annually with 5-year rolling averages
- Default year: 2022 (representing 2018-2022 data)

## Available Geographic Levels

The Census API supports various geographic levels. This integration uses:
- **ZIP Code Tabulation Areas (ZCTAs)**: Best for property-level analysis

## Troubleshooting

### Issue: "Invalid API Key" Error

**Solution**: Double-check that you copied the entire API key from the email. Make sure there are no extra spaces or line breaks.

### Issue: "Rate Limit Exceeded"

**Solution**:
- If using without a key: Register for a free API key (see above)
- If using with a key: Verify the key is correctly set in your `.env` file

### Issue: "No Data for ZIP Code"

**Solution**:
- Some ZIP codes may not have ACS 5-Year data available
- Try a different, well-populated ZIP code (e.g., 10001 for New York, 90210 for Los Angeles)
- ZCTA boundaries don't always match USPS ZIP codes exactly

### Issue: "Connection Timeout"

**Solution**:
- Check your internet connection
- The Census API may be temporarily down - try again later
- Verify the `CENSUS_API_BASE_URL` is correct in your `.env` file

## Additional Resources

- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [ACS 5-Year Data](https://www.census.gov/data/developers/data-sets/acs-5year.html)
- [Variable Search Tool](https://api.census.gov/data/2022/acs/acs5/variables.html)
- [Census Reporter](https://censusreporter.org/) - Visual exploration of Census data

## Support

For Census API issues:
- Email: census.api@census.gov
- [API User Group](https://groups.google.com/g/us-census-api)

For Aequitas platform issues:
- Contact your development team
