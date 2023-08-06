import os
from opencage.geocoder import OpenCageGeocode


class Country:
    def __init__(self):
        pass

    def get_country_name(self, location):
        # Create a geocoder instance
        api_key = os.getenv("RDS_OPENCAGE_KEY")

        # Define the city or state
        geocoder = OpenCageGeocode(api_key)

        # Use geocoding to get the location details
        results = geocoder.geocode(location)

        if results and len(results) > 0:
            first_result = results[0]
            components = first_result['components']

            # Extract the country from components
            country = components.get('country', '')
            if not country:
                # If country is not found, check for country_code as an alternative
                country = components.get('country_code', '')
            return country

        else:
            return None


if __name__ == "__main__":
    pass
