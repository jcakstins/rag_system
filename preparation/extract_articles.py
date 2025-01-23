"""Extract and save articles from a PDF file.

This script extracts articles from a specified PDF file and saves them as individual JSON files.
It identifies articles based on a specific pattern (e.g., 'Article 1.') and organizes the content accordingly.
"""

import pdfplumber
import re
import os
import json
from datetime import datetime
from pathlib import Path

def extract_articles(file_path: Path) -> list:
    """Extract articles from a PDF file.

    This function reads a PDF file, identifies articles based on a specific pattern (e.g., 'Article 1.'),
    and extracts their titles and content.

    :param file_path: The path to the PDF file to be processed.
    :type file_path: Path
    :return: A list of dictionaries, where each dictionary contains the title and content of an article.
    :rtype: list
    """
    def __process_page_text(page_text, current_article, articles):
        for line in page_text.split("\n"):
            if re.match(article_pattern, line):
                if current_article["title"]:  # Save the current article
                    articles.append(current_article)
                    current_article = {"title": None, "content": ""}
                current_article["title"] = line.strip()  # Start a new article
            else:
                current_article["content"] += f"{line.strip()} "

    articles = []
    current_article = {"title": None, "content": ""}
    article_pattern = re.compile(r"Article\s+\d+\.")

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            __process_page_text(page.extract_text(), current_article, articles)

        if current_article["title"]:  # Append the last article
            articles.append(current_article)

    return articles

def save_articles_as_json(articles: list, output_dir: Path, extraction_timestamp: datetime) -> None:
    """Save extracted articles as individual JSON files.

    This function takes a list of articles and saves each one as a JSON file in the specified output directory.
    Each JSON file includes the article number, title, content, and a timestamp of the extraction.

    :param articles: A list of dictionaries containing article metadata (title and content).
    :type articles: list
    :param output_dir: The directory where the JSON files will be saved.
    :type output_dir: Path
    :param extraction_timestamp: Timestamp (datetime) indicating when the pipeline run
    :type extraction_timestamp: datetime
    :return: None
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for article in articles:
        article_number = re.search(r"Article\s+(\d+)", article["title"]).group(1)
        file_name = f"article_{article_number}.json"
        article_metadata = {
            "article_number": article_number,
            "title": article["title"],
            "content": article["content"].strip(),
            "extraction_timestamp": extraction_timestamp.isoformat()
        }

        with open(os.path.join(output_dir, file_name), "w") as f:
            json.dump(article_metadata, f, indent=4)

if __name__ == '__main__':
    """Main entry point of the script.

    This script extracts articles from a specified PDF file and saves them as JSON files in the given directory.
    Update the `file_path` and `save_path` variables as needed before running.
    """
    file_path = Path("./data/raw/GDPR_Art_1_21.pdf")
    save_path = Path("./data/extracted_articles")
    current_datetime = datetime.now()
    articles = extract_articles(file_path)
    save_articles_as_json(articles, save_path, current_datetime)
