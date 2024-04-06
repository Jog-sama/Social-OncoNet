import pandas as pd
import requests
import json

from multiprocessing import Pool
from tqdm import tqdm
from bs4 import BeautifulSoup

import sys

sys.setrecursionlimit(25000)

def get_post(post):
    post_a = post.find('a')
    post_soup = BeautifulSoup(requests.get(post_a.get_attribute_list('href')[0]).content, 'html.parser')
    title = post_soup.find('div', attrs={'class': "PageTitle pageHeadingBox isLarge"}).text
    username = post_soup.find('span', attrs={'class': 'Author'}).text.replace("\n", '')
    date = post_soup.find('time').get_attribute_list('datetime')[0]
    content = post_soup.find('div', attrs={'class':'Message userContent'}).text
    try:
        comments = ["\n".join([item.text for item in comment_element.find('div', attrs={"class":'Message userContent'}).findAll('p')]) for comment_element in post_soup.find('ul', attrs={'class':'MessageList DataList Comments pageBox'}).findAll('li')]
    except:
        comments = []

    return {
        'title':title,
        'username':username,
        'date':date,
        'content':content,
        'comments':comments
    }

if __name__ == "__main__":
    page_url = "https://csn.cancer.org/categories"
    max_pages = 5
    n_processes = 10

    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    final_data = {}

    ul_element = soup.findAll('ul', attrs={"class":"DataList CategoryList pageBox"})[0]


    categories = ul_element.findAll('li')[3:]
    with Pool(n_processes) as pool:
        for category in categories:
            category_data = category.findAll('a')[1]
            category_link = category_data.get_attribute_list('href')[0]
            category_text = category_data.text

            final_data[category_text] = []

            for i in range(1, max_pages+1):
                try:
                    category_soup = BeautifulSoup(requests.get(f"{category_link}/p{i}").content, 'html.parser')
                    post_list = category_soup.findAll('ul', attrs={'class':'linkList'})
                    if post_list:
                        post_list = post_list[0]
                        posts = post_list.findAll('li')[1:]
                        posts_iterator = pool.imap(get_post, posts)
                        for post in tqdm(posts_iterator, f"{category_text}, page {i}", total=len(posts)):
                            final_data[category_text].append(post)
                    else:
                        print(f"No post list found for {category_text}, page {i}")
                except:
                    print(f"Error fetching {category_text}, page {i}: {e}")


            print(f'data extracted for {category_text}, length of data {len(final_data)}')
            print('first 5 samples')
            #print(json.dumps(final_data[category_text][:5], indent=4))

    json.dump(final_data, open('scraped_data.json', 'w'), indent=4)