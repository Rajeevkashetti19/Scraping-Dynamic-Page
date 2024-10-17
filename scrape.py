import requests
from bs4 import BeautifulSoup
import json

# URL for scraping jobs by country
country_template="https://jobs.citi.com/search-jobs/results?ActiveFacetID={industry}&CurrentPage=1&RecordsPerPage=10&Distance=50&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=False&CustomFacetName=&FacetTerm=&FacetType=0&FacetFilters%5B0%5D.ID={industry}&FacetFilters%5B0%5D.FacetType=5&FacetFilters%5B0%5D.Count={count}&FacetFilters%5B0%5D.Display={industry}&FacetFilters%5B0%5D.IsApplied=true&FacetFilters%5B0%5D.FieldName=industry&SearchResultsModuleName=SearchResults+-+Technology&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0&SearchType=6&PostalCode=&ResultsType=0&fc=&fl=&fcf=&afc=&afl=&afcf="

url_template = "https://jobs.citi.com/search-jobs/results?ActiveFacetID={id}&CurrentPage=1&RecordsPerPage=10&Distance=50&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=False&CustomFacetName=&FacetTerm=&FacetType=0&FacetFilters%5B0%5D.ID={id}&FacetFilters%5B0%5D.FacetType=2&FacetFilters%5B0%5D.Count={count}&FacetFilters%5B0%5D.Display={country}&FacetFilters%5B0%5D.IsApplied=true&FacetFilters%5B0%5D.FieldName=&SearchResultsModuleName=SearchResults+-+Technology&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0&SearchType=5&PostalCode=&ResultsType=0&fc=&fl=&fcf=&afc=&afl=&afcf="

city_template = "https://jobs.citi.com/search-jobs/results?ActiveFacetID={id}&CurrentPage=1&RecordsPerPage=10&Distance=50&RadiusUnitType=0&Keywords=&Location=&ShowRadius=False&IsPagination=False&CustomFacetName=&FacetTerm=&FacetType=0&FacetFilters%5B0%5D.ID={industry}&FacetFilters%5B0%5D.FacetType=5&FacetFilters%5B0%5D.Count=14&FacetFilters%5B0%5D.Display={industry}&FacetFilters%5B0%5D.IsApplied=true&FacetFilters%5B0%5D.FieldName=industry&FacetFilters%5B1%5D.ID={country_id}&FacetFilters%5B1%5D.FacetType=2&FacetFilters%5B1%5D.Count={country_count}&FacetFilters%5B1%5D.Display={country}&FacetFilters%5B1%5D.IsApplied=true&FacetFilters%5B1%5D.FieldName=&FacetFilters%5B2%5D.ID={id}&FacetFilters%5B2%5D.FacetType=3&FacetFilters%5B2%5D.Count={count}&FacetFilters%5B2%5D.Display={region}%2C+{country}&FacetFilters%5B2%5D.IsApplied=true&FacetFilters%5B2%5D.FieldName=&SearchResultsModuleName=SearchResults+-+Technology&SearchFiltersModuleName=Search+Filters&SortCriteria=0&SortDirection=0&SearchType=6&PostalCode=&ResultsType=0&fc=&fl=&fcf=&afc=&afl=&afcf="
# Function to fetch the list of countries from the main page

def fetch_cities_by_region(country_name,fileds,industry):
    country_encoded = country_name[0].replace(" ", "+")
    print(country_encoded)

    # Use the URL template with the encoded country name
    url = city_template.format(country=country_encoded, country_count =country_name[1],country_id=country_name[2],region=fileds[0],id=fileds[2],count=fileds[1],industry=industry)

    # Send the GET request to f
    # etch the page
    response = requests.get(url)
    data = json.loads(response.text)
    html_content = data["filters"]

# Clean up the string to make it a valid HTML
    html_content = html_content.replace('\"', '').replace('\r\n', '').replace('  ', ' ').strip()

# Parse the cleaned HTML
    soup = BeautifulSoup(html_content, "html.parser")
    region_section = soup.find('button', {'id': 'city-toggle'})


    # Navigate to the parent section and then to the <ul> containing countries
    region_list = region_section.find_next('ul', class_='search-filter-list')

    # List to store country names
    cities = []

    # Loop through each <li> element and extract the country name
    for li in region_list.find_all('li'):
        try:
            # Extract the country name from the <span> with class 'filter__facet-name'
            city_name=li.find('span', class_='filter__facet-name').text.strip()
            cities.append(city_name)
            
        except AttributeError:
            # Skip if there is no country name found
            continue
    return cities


def fetch_industry():
    url = "https://jobs.citi.com/search-jobs"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # print(soup.prettify())

    industry_section = soup.find('button', {'id': 'industry-toggle'})
    industry_list = industry_section.find_next('ul', class_='search-filter-list')

    # List to store country names
    industry_names = []

    # Loop through each <li> element and extract the country name
    for li in industry_list.find_all('li'):
        fileds=[]
        try:
            # Extract the country name from the <span> with class 'filter__facet-name'
            # country_name = li.find('span', class_='filter__facet-name').text.strip()
            fileds.append(li.find('span', class_='filter__facet-name').text.strip()) # Country name
            fileds.append(li.find('span', class_='filter__facet-count').text.strip())  # Count
            fileds.append(li.find('input')['data-id'])
            print(fileds)
            # print(count)
            industry_names.append(fileds)
        except AttributeError:
            # Skip if there is no country name found
            continue
    print(len(industry_names))
    return industry_names

def fetch_country_list():
    url = "https://jobs.citi.com/search-jobs"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    # print(soup.prettify())

    industry_section = soup.find('button', {'id': 'industry-toggle'})
    country_list = country_section.find_next('ul', class_='search-filter-list')

    # List to store country names
    country_names = []

    # Loop through each <li> element and extract the country name
    for li in country_list.find_all('li'):
        fileds=[]
        try:
            # Extract the country name from the <span> with class 'filter__facet-name'
            # country_name = li.find('span', class_='filter__facet-name').text.strip()
            fileds.append(li.find('span', class_='filter__facet-name').text.strip()) # Country name
            fileds.append(li.find('span', class_='filter__facet-count').text.strip())  # Count
            fileds.append(li.find('input')['data-id'])
            print(fileds)
            # print(count)
            country_names.append(fileds)
        except AttributeError:
            # Skip if there is no country name found
            continue
    print(len(country_names))
    return country_names

    #Find the section where the country-toggle button is present
    country_section = soup.find('button', {'id': 'country-toggle'})

    # Navigate to the parent section and then to the <ul> containing countries
    country_list = country_section.find_next('ul', class_='search-filter-list')

    # List to store country names
    country_names = []

    # Loop through each <li> element and extract the country name
    for li in country_list.find_all('li'):
        fileds=[]
        try:
            # Extract the country name from the <span> with class 'filter__facet-name'
            # country_name = li.find('span', class_='filter__facet-name').text.strip()
            fileds.append(li.find('span', class_='filter__facet-name').text.strip()) # Country name
            fileds.append(li.find('span', class_='filter__facet-count').text.strip())  # Count
            fileds.append(li.find('input')['data-id'])
            print(fileds)
            # print(count)
            country_names.append(fileds)
        except AttributeError:
            # Skip if there is no country name found
            continue
    print(len(country_names))
    return country_names

# Function to fetch regions for each country
def fetch_regions_for_country(country_name,industry):
    # Replace spaces with "+" in the country name for URL encoding
    country_encoded = country_name[0].replace(" ", "+")
    print(country_encoded)

    # Use the URL template with the encoded country name
    url = url_template.format(country=country_encoded, count =country_name[1],id=country_name[2])

    # Send the GET request to f
    # etch the page
    response = requests.get(url)
    data = json.loads(response.text)
    html_content = data["filters"]

# Clean up the string to make it a valid HTML
    html_content = html_content.replace('\"', '').replace('\r\n', '').replace('  ', ' ').strip()

# Parse the cleaned HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # soup = BeautifulSoup(response.content, "html.parser")

    # print(soup.prettify('button'))


    region_section = soup.find('button', {'id': 'region-toggle'})


    # Navigate to the parent section and then to the <ul> containing countries
    region_list = region_section.find_next('ul', class_='search-filter-list')

    # List to store country names
    regions = {}

    # Loop through each <li> element and extract the country name
    for li in region_list.find_all('li'):
        fields=[]
        try:
            # Extract the country name from the <span> with class 'filter__facet-name'
            fields.append(li.find('span', class_='filter__facet-name').text.strip()) # Country name
            fields.append(li.find('span', class_='filter__facet-count').text.strip())  # Count
            fields.append(li.find('input')['data-id'])
            print(fields)
            regions[fields[0]]=fetch_cities_by_region(country_name,fields,industry)
            regions.append(region_name)
            
        except AttributeError:
            # Skip if there is no country name found
            continue

    # regions = []
    
    # # Parse the region elements (adjust selectors based on actual HTML)
    # region_elements = soup.select("ul.search-filter-list.expandable-childlist-open > li")
    # for region in region_elements:
    #     try:
    #         label = region.find("label")
    #         region_name = label.find("span", class_="filter__facet-name").text.strip()
    #         if region_name:
    #             regions.append(region_name)
    #     except Exception as e:
    #         print(f"Could not extract region for {country_name}: {e}")
    print(regions)
    
    return regions

def fetch_countries_and_regions(industry_name):
    # Replace spaces with "+" in the country name for URL encoding
    industry_encoded = industry_name[0].replace(" ", "+")

    # Use the URL template with the encoded country name
    url = country_template.format(industry=industry_encoded, count =industry_name[1])

    # Send the GET request to f
    # etch the page
    response = requests.get(url)
    data = json.loads(response.text)
    html_content = data["filters"]

    # Clean up the string to make it a valid HTML
    html_content = html_content.replace('\"', '').replace('\r\n', '').replace('  ', ' ').strip()

    # Parse the cleaned HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # soup = BeautifulSoup(response.content, "html.parser")

    # print(soup.prettify('button'))


    region_section = soup.find('button', {'id': 'country-toggle'})

    print(region_section)

    # Navigate to the parent section and then to the <ul> containing countries
    region_list = region_section.find_next('ul', class_='search-filter-list')

    # List to store country names
    countries = {}

    # Loop through each <li> element and extract the country name
    for li in region_list.find_all('li'):

        fileds=[]
        try:
            # Extract the country name from the <span> with class 'filter__facet-name'
            # country_name = li.find('span', class_='filter__facet-name').text.strip()
            fileds.append(li.find('span', class_='filter__facet-name').text.strip()) # Country name
            fileds.append(li.find('span', class_='filter__facet-count').text.strip())  # Count
            fileds.append(li.find('input')['data-id'])
            print(fileds)
            countries[fileds[0]]=fetch_regions_for_country(fileds, industry_encoded)
            # print(count)
        except AttributeError:
            continue
            # Skip if the
        # try:
        #     # Extract the country name from the <span> with class 'filter__facet-name'
        #     region_name = li.find('span', class_='filter__facet-name').text.strip()
        #     regions.append(region_name)
        # except AttributeError:
        #     # Skip if there is no country name found
        #     continue


    # print(regions)
    return countries

def main():
    # Step 1: Fetch country names
    industries = fetch_industry()
    countries_by_industry={}

    for industry in industries:
        print(f"Fetching regions for {industry}...")
        countries = fetch_countries_and_regions(industry)
        countries_by_industry[industry[0]] = countries

    # # Step 3: Output results
    # for country, regions in regions_by_country.items():
    #     print(f"{country}: {', '.join(regions)}")

    # # Optionally, write the results to a file
    # with open("countries_and_regions.txt", "w") as f:
    #     for country, regions in regions_by_country.items():
    #         f.write(f"{country}: {', '.join(regions)}\n")
    # countries = fetch_country_list()

    # # Dictionary to store countries and corresponding regions
    # regions_by_country = {}

    # # Step 2: Loop through each country and fetch its regions
    # for country in countries:
    #     print(f"Fetching regions for {country}...")
    #     regions = fetch_regions_for_country(country)
    #     regions_by_country[country[0]] = regions

    # # Step 3: Output results
    # for country, regions in regions_by_country.items():
    #     print(f"{country}: {', '.join(regions)}")

    # # Optionally, write the results to a file
    # with open("countries_and_regions.txt", "w") as f:
    #     for country, regions in regions_by_country.items():
    #         f.write(f"{country}: {', '.join(regions)}\n")
    print(countries_by_industry)

if __name__ == "__main__":
    main()
