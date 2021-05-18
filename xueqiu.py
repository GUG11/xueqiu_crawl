from dataclasses import dataclass
from datetime import datetime, date

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
"""
python3 -m pip install webdriver_manager
"""
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class Post(object):
    user_name: str
    link: str
    content_text: str
    time: datetime

    def __str__(self):
        return f'[{self.time}]{self.user_name}: {self.content_text}({self.link})'


def get_posts_of_current_user(driver):
    elem = driver.find_element_by_class_name('profiles__timeline__bd')
    posts = elem.find_elements_by_class_name('timeline__item__main')
    posts = list(map(get_post_info, posts))
    return posts

def get_post_info(post_item_main):
    user_name = post_item_main.find_element_by_class_name('user-name')
    metadata = post_item_main.find_element_by_class_name('date-and-source')
    link = metadata.get_attribute('href')
    post_date, post_time = metadata.text.split(' ')[0:2]
    if len(post_date) < 6:
        post_date = f'{date.today().year}-{post_date}'
    content = post_item_main.find_element_by_class_name('timeline__item__content')
    return Post(
        user_name=user_name.text,
        link=link,
        content_text=content.text,
        time=datetime.strptime(f'{post_date} {post_time}', '%Y-%m-%d %H:%M')
    )


def rank(posts):
    posts.sort(reverse=True, key=lambda post: post.time)

if __name__ == '__main__':
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get('https://xueqiu.com/u/7291654456#/follow')
    profile_users_container = driver.find_element_by_class_name('profiles__users')
    followee_user_cards = profile_users_container.find_elements_by_class_name('user-name')
    followee_links = list(
        map(lambda elem: elem.get_attribute('href'), followee_user_cards)
    )
    posts_by_followees = {}
    for link in followee_links:
        driver.get(link)
        posts_by_followees[link] = get_posts_of_current_user(driver)
    driver.quit()

    all_posts = []
    for link, posts in posts_by_followees.items():
        for post in posts:
            all_posts.append(post)

    rank(all_posts)
    for post in all_posts:
        print(post)
