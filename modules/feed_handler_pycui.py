"""Handles RSS feed parsing, article extraction, and bookmark management."""

from datetime import datetime
import feedparser as fp
from trafilatura import fetch_url, extract

MAX_HEADLINES = 80

fp.USER_AGENT = "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.166 Safari/537.36"
feed_dict = {}
bookmarks_dict = {}

def add_feed(url: str, title:str= None) -> dict:
    """Parse and add a new RSS feed from the given URL.
    
    Returns:
        A dictionary containing feed details (title, URL, headlines),
        or a string error message if the feed cannot be parsed.
    """
    
    time_now = datetime.now()

    try:
        rss = fp.parse(url)

        if rss.feed:
            if len(rss.feed.title) > 0:
                feed_title = rss.feed.title
            else:
                return 'Cannot parse feed - No title found'

            if feed_title in feed_dict and not title:
                return 'Duplicate entry'

            if not title:
                feed_dict[feed_title] = {}
                feed_dict[feed_title]['title'] = feed_title
                feed_dict[feed_title]['url'] = url

            feed_dict[feed_title]['last_updated'] = time_now.strftime("%a %d %b %Y %H:%M")
            feed_dict[feed_title]['headlines'] = {}

            for i, entry in enumerate(rss.entries[:MAX_HEADLINES]):
                headline = rss.entries[i].title
                feed_dict[feed_title]['headlines'][headline] = rss.entries[i].link

            return feed_dict[feed_title]
        else:
            return 'Feed not found'

    except Exception as error:
        return error

def set_interval(refresh_time: str):
    """Add a global refresh interval for feeds in minutes. Stores it in feed_dict as an int"""
    try:
        feed_dict['refresh_interval'] = int(refresh_time)
    except ValueError:
        feed_dict['refresh_interval'] = 0

def get_refresh_status(time_str: int) -> bool:
    """ Determines whether the currently selected feeds last_updated>refresh_interval
        by comparing feed['last_updated'] against datetime.now()
        and converting the delta seconds into minutes.

        Arguement:
            The time_str: Current feeds last refresh time as an int
        
        Returns:
            True if refresh is due or False if not.
    """
    time_now = datetime.now()

    if 'refresh_interval' in feed_dict.keys() and feed_dict['refresh_interval'] != 0:
        interval = feed_dict['refresh_interval']
    else:
        return False

    last_update = datetime.strptime(time_str, "%a %d %b %Y %H:%M")
    diff = time_now - last_update
    diff_minutes = diff.total_seconds() / 60
    return diff_minutes > interval

def add_bookmark(title: str, url:str) -> bool :
    """Add a bookmark for the given article if it doesn't already exist.
        
        Returns:
            True if the bookmark was added, False if it already exists.
        """    
    if not title in bookmarks_dict:
        bookmarks_dict[title] = url
        return True
    else:
        return False

def get_article(url: str) -> str:
    """Fetch and extract the main article content from a given URL.
    
    Returns:
        The article text in Markdown format.
    """
    return extract(fetch_url(url), output_format = 'markdown')
