import { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { DivIcon } from 'leaflet';
import type { LatLngExpression } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { DemographicData } from '../types/census';

interface Property {
  id: number;
  lat: number;
  lng: number;
  price: string;
  address: string;
  zipcode?: string;
  demographics?: DemographicData;
  demographicsLoading?: boolean;
  demographicsError?: string;
}

interface PropertyMapProps {
  properties?: Property[];
  center?: LatLngExpression;
  zoom?: number;
  className?: string;
}

// Helper function to extract ZIP code from address
const extractZipCode = (address: string): string | null => {
  const zipMatch = address.match(/\b\d{5}\b/);
  return zipMatch ? zipMatch[0] : null;
};

// Mock property data around Sacramento, CA
const defaultProperties: Property[] = [
  {
    id: 1,
    lat: 38.5816,
    lng: -121.4944,
    price: '$625k',
    address: '1234 Capitol Mall, Sacramento, CA 95814',
    zipcode: '95814'
  },
  {
    id: 2,
    lat: 38.5950,
    lng: -121.4750,
    price: '$495k',
    address: '456 Folsom Blvd, Sacramento, CA 95819',
    zipcode: '95819'
  },
  {
    id: 3,
    lat: 38.5680,
    lng: -121.5050,
    price: '$550k',
    address: '789 Land Park Dr, Sacramento, CA 95818',
    zipcode: '95818'
  },
  {
    id: 4,
    lat: 38.6100,
    lng: -121.4600,
    price: '$720k',
    address: '321 Fair Oaks Blvd, Sacramento, CA 95825',
    zipcode: '95825'
  },
  {
    id: 5,
    lat: 38.5500,
    lng: -121.4700,
    price: '$580k',
    address: '987 Riverside Blvd, Sacramento, CA 95822',
    zipcode: '95822'
  }
];

const PropertyMap = ({
  properties = defaultProperties,
  center = [38.5816, -121.4944],
  zoom = 12,
  className = 'h-full w-full'
}: PropertyMapProps) => {
  const [propertyDemographics, setPropertyDemographics] = useState<Record<number, DemographicData | null>>({});
  const [loadingDemographics, setLoadingDemographics] = useState<Record<number, boolean>>({});

  // Fetch demographics for a property
  const fetchDemographicsForProperty = async (property: Property) => {
    const zipcode = property.zipcode || extractZipCode(property.address);
    if (!zipcode || loadingDemographics[property.id] || propertyDemographics[property.id]) {
      return;
    }

    setLoadingDemographics(prev => ({ ...prev, [property.id]: true }));

    try {
      const response = await fetch(`/api/v1/demographics/${zipcode}`);
      if (response.ok) {
        const result = await response.json();
        if (result.success && result.data) {
          setPropertyDemographics(prev => ({ ...prev, [property.id]: result.data }));
        }
      }
    } catch (error) {
      console.error(`Failed to fetch demographics for ${zipcode}:`, error);
    } finally {
      setLoadingDemographics(prev => ({ ...prev, [property.id]: false }));
    }
  };

  // Create custom marker icon using Tailwind classes
  const createCustomIcon = (price: string): DivIcon => {
    return new DivIcon({
      className: 'custom-marker',
      html: `
        <div class="bg-red-700 text-white rounded-full px-2 py-1 text-xs font-bold shadow-lg cursor-pointer hover:bg-red-800 transition-colors whitespace-nowrap">
          ${price}
        </div>
      `,
      iconSize: [60, 30],
      iconAnchor: [30, 15],
      popupAnchor: [0, -15]
    });
  };

  return (
    <div className={className}>
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="h-full w-full z-0 rounded-xl"
        zoomControl={true}
        attributionControl={false}
      >
        {/* CartoDB Voyager tile layer - clean and professional */}
        <TileLayer
          attribution=''
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          maxZoom={20}
        />

        {/* Render custom markers for each property */}
        {properties.map((property) => {
          const demographics = propertyDemographics[property.id];
          const isLoading = loadingDemographics[property.id];

          return (
            <Marker
              key={property.id}
              position={[property.lat, property.lng]}
              icon={createCustomIcon(property.price)}
              eventHandlers={{
                popupopen: () => fetchDemographicsForProperty(property)
              }}
            >
              <Popup className="custom-popup" minWidth={280}>
                <div className="p-3">
                  <p className="font-semibold text-gray-800 text-base">
                    {property.price}
                  </p>
                  <p className="text-gray-600 text-sm mt-1">
                    {property.address}
                  </p>

                  {/* Demographics Section */}
                  {isLoading && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs text-gray-500">Loading demographics...</p>
                    </div>
                  )}

                  {demographics && !isLoading && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-xs font-semibold text-gray-700 mb-2">Market Demographics</p>
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">Median Income:</span>
                          <span className="font-medium">${demographics.income.medianHouseholdIncome.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">60% AMI:</span>
                          <span className="font-medium">${demographics.income.ami60Percent.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">Median Rent:</span>
                          <span className="font-medium">${demographics.housing.medianGrossRent.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">Households:</span>
                          <span className="font-medium">{demographics.population.totalHouseholds.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-600">Occupancy Rate:</span>
                          <span className="font-medium">{demographics.housing.occupancyRate}%</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default PropertyMap;
