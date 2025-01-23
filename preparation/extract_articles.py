import pdfplumber
import re
import os
import json
from datetime import datetime
from pathlib import Path

def extract_articles(file_path: Path)-> dict:
    articles = []
    current_article = {"title": None, "content": ""}
    
    article_pattern = re.compile(r"Article\s+\d+\.")
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            for line in text.split("\n"):
                if re.match(article_pattern, line):
                    if current_article["title"]:  # Save the current article
                        articles.append(current_article)
                        current_article = {"title": None, "content": ""}
                    current_article["title"] = line.strip()  # Start a new article
                else:
                    current_article["content"] += f"{line.strip()} "
                    
        if current_article["title"]:  # Append the last article
            articles.append(current_article)
    
    return articles


def save_articles_as_json(articles: dict, output_dir: Path)-> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for article in articles:
        article_number = re.search(r"Article\s+(\d+)", article["title"]).group(1)
        file_name = f"article_{article_number}.json"
        article_metadata = {
            "article_number": article_number,
            "title": article["title"],
            "content": article["content"].strip(),
            "extraction_timestamp": datetime.now().isoformat()
        }
        
        with open(os.path.join(output_dir, file_name), "w") as f:
            json.dump(article_metadata, f, indent=4)


if __name__=='__main__':
    file_path = Path("./data/raw/GDPR_Art_1_21.pdf")
    save_path = Path("./data/extracted_articles")
    articles = extract_articles(file_path)
    save_articles_as_json(articles, save_path)