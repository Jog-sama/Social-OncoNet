import json
import re
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import csv

# Download necessary resources if not already downloaded
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')

# Initialize WordNet lemmatizer
lemmatizer = WordNetLemmatizer()

# Load stopwords
stop_words = set(stopwords.words('english'))

# Function to preprocess text
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special symbols and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize text
    tokens = nltk.word_tokenize(text)
    # Lemmatize tokens
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    # Remove stopwords
    filtered_tokens = [word for word in lemmatized_tokens if word not in stop_words]
    # Join tokens back to form text
    processed_text = ' '.join(filtered_tokens)
    return processed_text

# Load JSON data
with open('scraped_data.json', 'r') as f:
    data = json.load(f)

# Preprocess data and store in a list of dictionaries
preprocessed_data = []

for cancer_type, posts in data.items():
    for post_data in posts:
        processed_post_data = {}
        processed_post_data['cancer_type'] = cancer_type
        processed_post_data['title'] = post_data['title']
        processed_post_data['username'] = post_data['username']
        processed_post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y-%m-%d %H:%M:%S')
        processed_post_data['content'] = preprocess_text(post_data['content'])
        processed_post_data['comments'] = [preprocess_text(comment) for comment in post_data['comments']]
        preprocessed_data.append(processed_post_data)

# Write preprocessed data to a CSV file
output_file = 'preprocessed_data.csv'
fieldnames = ['cancer_type', 'title', 'username', 'date', 'content', 'comments']

with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for post_data in preprocessed_data:
        writer.writerow(post_data)

print(f"Preprocessed data saved to {output_file}")