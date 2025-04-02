# pip install scrapy tqdm

import os
import scrapy
from scrapy.crawler import CrawlerProcess
from tqdm import tqdm  # Import tqdm for the progress bar
import argparse

class USAJobsHTMLSpider(scrapy.Spider):
    name = "usajobs_batch_scraper"

    # Adjust concurrency settings
    def __init__(self, job_ids, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job_ids = job_ids
        os.makedirs("job_html", exist_ok=True)  # Ensure directory exists
        self.progress_bar = tqdm(total=len(job_ids), desc="Scraping Job IDs", unit="job")  # Initialize progress bar

    # Start requests
    def start_requests(self):
        base_url = "https://www.usajobs.gov/job/{}/print"
        for job_id in self.job_ids:
            url = base_url.format(job_id)
            yield scrapy.Request(
                url, 
                callback=self.save_html, 
                meta={'job_id': job_id}, 
                errback=self.handle_error
            )

    # Save HTML
    def save_html(self, response):
        job_id = response.meta['job_id']
        file_path = f"job_html/usa_jobs_{job_id}.html"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(response.text)

        self.log(f"Saved: {file_path}")
        self.progress_bar.update(1)  # Update progress bar after each job is saved

    # Handle errors: if a job fails, save the job ID
    def handle_error(self, failure):
        """Log failed job ID for later reprocessing."""
        job_id = failure.request.meta['job_id']
        
        with open("failed_jobID.txt", "a", encoding="utf-8") as f:
            f.write(f"{job_id}\n")  # Save one failed job ID per line
        
        self.log(f" Job ID {job_id} failed and saved to failed_jobID.txt")
        self.progress_bar.update(1)  # Update progress bar even for failed jobs

    def closed(self, reason):
        """Close the progress bar when the spider is done."""
        self.progress_bar.close()

# Function to read job control numbers from a file    
def read_job_control_numbers(file_name):
    with open(file_name) as f:
        job_control_number_list = f.read().splitlines()
    return [int(i) for i in job_control_number_list]  # Convert all job control number to int

# Main function to parse arguments and run the scraper
def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Scrape USAJobs data.')
    parser.add_argument('file_name', help='The name of the job control number list file')
    args = parser.parse_args()

    # Read job control numbers from the provided file
    job_control_number_list = read_job_control_numbers(args.file_name)
    
    total_jobs_count = len(job_control_number_list) 
    print("Total number of jobs:", total_jobs_count)

    # Function to Run Scrapy with Optimized Settings
    download_html_batch(job_control_number_list)

# Function to Run Scrapy with Optimized Settings
def download_html_batch(job_ids, concurrent_requests=20):
    process = CrawlerProcess(settings={
        "CONCURRENT_REQUESTS": concurrent_requests,
        "DOWNLOAD_DELAY": 2,  # Fixed delay (Scrapy auto-randomizes)
        "AUTOTHROTTLE_ENABLED": True,  # Dynamically adjusts request speed
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 5,
        "LOG_LEVEL": "WARNING",  # Less spammy logs, if want all, use INFO
        "COOKIES_ENABLED": False,  # Reduces tracking risk
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    })
    
    process.crawl(USAJobsHTMLSpider, job_ids=job_ids)
    process.start()  # Start Scrapy

# Run the script
if __name__ == "__main__":
    main()

# Run the script with:
# python full_scraper.py job_control_number_list.txt
