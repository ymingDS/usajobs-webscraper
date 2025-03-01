import requests
from bs4 import BeautifulSoup
import json
import re

def get_job_id_from_url(url):
    """Extracts the job ID from the URL."""
    match = re.search(r'/job/(\d+)', url)
    return match.group(1) if match else None

def scrape_usajobs(url):
    """Scrapes job information from a USAJobs URL and saves it in JSON format."""
    
    # Extract the job ID
    job_id = get_job_id_from_url(url)
    if not job_id:
        print("Invalid URL: Job ID not found.")
        return
    
    # Send a request to the URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data, status code: {response.status_code}")
        return
    
    # Parse the page content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize a dictionary to store job information
    job_data = {}
    
    # Find job title
    title = soup.find('h1', class_='usajobs-joa-banner__title')
    job_data['title'] = title.get_text(strip=True) if title else "N/A"
    
    # Find the agency name or organization
    agency = soup.find('div', class_='usajobs-joa-banner__dept')
    job_data['department'] = agency.get_text(strip=True) if agency else "N/A"
    
    # Find job location
    location = soup.find('span', class_='location')
    job_data['location'] = location.get_text(strip=True) if location else "N/A"
    
    # Find salary range
    salary = soup.find('span', class_='salary')
    job_data['salary'] = salary.get_text(strip=True) if salary else "N/A"
    
    overview = {}
    overview_all = soup.find('h2', id='overview')
    # Iterate over the next siblings of the overview header
    # Iterate over the next siblings of the overview header
    for sibling in overview_all.next_siblings:
        if sibling.name:  # Check if sibling is a tag (to skip NavigableString objects)
            # Loop through all <li> tags within the sibling
            for li in sibling.find_all('li', recursive=False):  # Only direct <li> children
                header = li.find('h3')
                key = header.get_text(strip=True) if header else li.name
                
                # Get all text content within <li>, excluding <h3> if it exists
                if header:
                    header.extract()  # Remove <h3> from <li> to avoid duplicating in value
                value = li.get_text(strip=True)
                
                # Store the key-value pair in the overview dictionary
                overview[key] = value
    job_data['overview'] = overview

    # Find job summary or description
    summary = soup.find('div', id='summary')
    job_data['summary'] = summary.get_text(strip=True) if summary else "N/A"

    # Find job sduties
    duties = soup.find('ul', class_='usajobs-list-bullets')
    job_data['duties'] = duties.get_text(strip=True) if duties else "N/A"

    requirements = {}

    # Find the requirements section by id
    requirements_section = soup.find('div', id='requirements')
    for child in requirements_section.children:
        # Check if the child is a tag (skip over strings and other elements)
        if child.name:
            header = child.find('h3')
            content = child.get_text(strip=True) if child else ""
            
            # Use the header text as key if available, otherwise use tag name
            key = header.get_text(strip=True) if header else child.name
            requirements[key] = content
    
    # Store the requirements data in job_data
    job_data['requirements'] = requirements

    evaluation = soup.find('div', id = 'how-you-will-be-evaluated')
    job_data['evaluation'] = evaluation.get_text(strip=True) if evaluation else "N/A"

    required_docs = soup.find('div', id = 'required-documents')
    job_data['required_docs'] = required_docs.get_text(strip=True) if required_docs else "N/A"

    apply = soup.find('div', id = 'how-to-apply')
    job_data['apply'] = apply.get_text(strip=True) if apply else "N/A"



    data = {job_id: job_data}
    
    # Save to a JSON file
    with open(f"{job_id}_job_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)
    
    print(f"Job data saved to {job_id}_job_data.json")

# Example usage
scrape_usajobs("https://www.usajobs.gov/job/591701000")
scrape_usajobs("https://www.usajobs.gov/job/672307500")
scrape_usajobs("https://www.usajobs.gov/job/647260900")
# 672307500, 647260900, 720439800, 540012100, 644461900, 609604700, 521002200, 545285700, 596622200, 765311000