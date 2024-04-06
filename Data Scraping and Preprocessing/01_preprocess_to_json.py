import json
import re
from datetime import datetime
import nltk
from nltk.corpus import stopwords

# Download stopwords if not already downloaded
nltk.download('stopwords')

# Load stopwords
stop_words = set(stopwords.words('english'))

# Function to preprocess text
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special symbols and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Remove stopwords
    tokens = nltk.word_tokenize(text)
    filtered_tokens = [word for word in tokens if word not in stop_words]
    # Join tokens back to form text
    processed_text = ' '.join(filtered_tokens)
    return processed_text

# Load JSON data
with open('scraped_data.json', 'r') as f:
    data = json.load(f)

# Preprocess data and store in a new dictionary
preprocessed_data = {}

for cancer_type, posts in data.items():
    preprocessed_data[cancer_type] = []
    for post_data in posts:
        processed_post_data = {}
        processed_post_data['title'] = post_data['title']
        processed_post_data['username'] = post_data['username']
        processed_post_data['date'] = datetime.strptime(post_data['date'], '%Y-%m-%dT%H:%M:%S+00:00').strftime('%Y-%m-%d %H:%M:%S')
        processed_post_data['content'] = preprocess_text(post_data['content'])
        processed_post_data['comments'] = [preprocess_text(comment) for comment in post_data['comments']]
        preprocessed_data[cancer_type].append(processed_post_data)

# Write preprocessed data to a new JSON file
output_file = 'preprocessed_data.json'
with open(output_file, 'w') as f:
    json.dump(preprocessed_data, f, indent=4)

print(f"Preprocessed data saved to {output_file}")
