""" 
To Do 
-----

 - Look at handling HTTP errors in feed_handler
 - OPML export
 
"""
__version__ = "1.1.0"

import curses
import os
import py_cui
import subprocess
import modules.feed_handler_pycui as fh
import modules.file_handler as files
import modules.gemini_AI_handler as ai

class Interface:

    def __init__(self, root: py_cui.PyCUI):
        """ Sets up PyCUI widgets and applies keybindings """
        self.current_feed = {}
        self.root = root

        ## Menus ##
        self.pub_menu = self.root.add_scroll_menu('Feeds', 0, 0, row_span = 3, column_span = 2)
        self.bookmarks_menu = self.root.add_scroll_menu('Bookmarks', 3, 0, row_span = 3, column_span = 2)
        self.link_menu = self.root.add_scroll_menu('Articles', 0, 2, row_span = 6, column_span = 6)
        self.feed_status = self.root.add_block_label('', 6, 2, row_span = 1, column_span = 2)
        self.new_feed_text = self.root.add_text_box('Add Feed', 6, 0, row_span = 1, column_span = 2)

        ## Buttons ##
        self.btn_save =  self.root.add_button('Save All', 6, 5, command = self.save_state)
        self.btn_refresh = self.root.add_button('Set refresh interval', 6, 6, column_span = 2,command = self.set_refresh_interval)

        ## Key bindings ##
        self.root.add_key_command(py_cui.keys.KEY_H_LOWER, self.show_help)
        self.root.add_key_command(py_cui.keys.KEY_S_LOWER, self.save_state)
        self.root.add_key_command(py_cui.keys.KEY_R_LOWER, self.refresh_feed)

        self.new_feed_text.add_key_command(py_cui.keys.KEY_ENTER, self.add_feed)

        self.pub_menu.add_key_command(py_cui.keys.KEY_D_LOWER, self.delete_feed)
        self.pub_menu.add_key_command(py_cui.keys.KEY_ENTER, self.show_articles)
        self.pub_menu.add_key_command(py_cui.keys.KEY_R_LOWER, self.refresh_feed)

        self.link_menu.add_key_command(py_cui.keys.KEY_T_LOWER, self.tl_dr)
        self.link_menu.add_key_command(py_cui.keys.KEY_B_LOWER, self.add_bookmark)
        self.link_menu.add_key_command(py_cui.keys.KEY_ENTER, self.get_article)
        self.link_menu.add_key_command(py_cui.keys.KEY_R_LOWER, self.refresh_feed)
        self.link_menu.add_key_command(py_cui.keys.KEY_X_LOWER, self.export_article_popup)

        self.bookmarks_menu.add_key_command(py_cui.keys.KEY_T_LOWER, self.tl_dr)
        self.bookmarks_menu.add_key_command(py_cui.keys.KEY_ENTER, self.get_bookmark)
        self.bookmarks_menu.add_key_command(py_cui.keys.KEY_D_LOWER, self.delete_bookmark)
        self.bookmarks_menu.add_key_command(py_cui.keys.KEY_X_LOWER, self.export_article_popup)

    def add_feed(self, target: str = None, title: str = None):
        """ Add a new RSS feed to feedhandler.feeddict. 'target' and 'title' specifies an existing feed to refresh. """
        url = self.new_feed_text.get().strip() if not target else target
        if len(url) > 0:

            if title:
                self.current_feed = fh.add_feed(url, title)
            else:
                self.current_feed = fh.add_feed(url)
                
            if type(self.current_feed) != str:
                if not target:
                    # Pass the feed title to feed_haddler.add_item to signify that the feed exists in feed_dict.
                    self.pub_menu.add_item(self.current_feed['title'])
                    idx = self.get_menu_length(self.pub_menu) - 1
                    self.pub_menu.set_selected_item_index(idx)
                self.show_articles(target)
            else:
                self.show_error_message(self.current_feed)                   
        self.new_feed_text.clear()

    def delete_feed(self):
        """Delete the currently selected feed from the list and feed dictionary."""
        selection = self.pub_menu.get()
        self.pub_menu.remove_selected_item()
        del fh.feed_dict[selection]

        if self.get_menu_length(self.pub_menu) > 0:
            self.show_articles()
        else:
            self.link_menu.clear()
            self.link_menu.set_title('Articles')

    def refresh_feed(self):
        """Reload the selected feed and update its headlines."""
        url = self.current_feed['url']
        title = self.current_feed['title']
        self.current_feed['headlines'] = {}
        self.add_feed(url, title)

    def set_refresh_interval(self):
        """ Set the global refresh interval for all feeds """
        self.root.show_text_box_popup('Enter global refresh interval time in minutes (0 to disable):', self.update_refresh_status)

    def update_refresh_status(self, t):
        """ Changes the title text on bt_refresh to reflect the current refresh interval """
        self.btn_refresh.set_title(f"Set refresh interval ({t} mins)")
        fh.set_interval(t)
        
    def show_articles(self, target: str = None):
        """Display the list of article headlines for the selected feed."""
        self.link_menu.clear()

        if not target:
            self.current_feed = fh.feed_dict[self.pub_menu.get()]

        if fh.get_refresh_status(self.current_feed['last_updated']):
            self.refresh_feed()
        else:
            self.link_menu.set_title(f"{self.pub_menu.get()} ({len(self.current_feed['headlines'].keys())})")
            headlines = [h for h in self.current_feed['headlines'].keys()]
            self.link_menu.add_item_list(headlines)
            self.feed_status.set_title(f"Feed last updated:\n{(self.current_feed['last_updated'])}")

        if 'refresh_interval' in fh.feed_dict.keys(): self.update_refresh_status(fh.feed_dict['refresh_interval'])

    def get_article(self):
        """Open the selected article from the current feed."""
        url = self.current_feed['headlines'][self.link_menu.get()]
        self.read_article(url)

    def get_bookmark(self):
        """Open the selected bookmarked article."""
        url = fh.bookmarks_dict[self.bookmarks_menu.get()]
        self.read_article(url)

    def read_article(self, url: str):
        """Display the article content in Glow for Markdown viewing."""
        """ Use Glow in a blocking subproces to render the selected feed of bookmark """
        story_text  = fh.get_article(url)
        self.do_glow_text(story_text)

    def do_glow_text(self, text:str):
        """ Takes a string and passes it to Glow in a blocking subprocee """
        curses.endwin()
        subprocess.run(['glow','-p'], input = text, text = True)
        os.system('reset')
        
    def add_bookmark(self):
        """Bookmark the currently selected article."""
        headline = self.link_menu.get()
        url = self.current_feed['headlines'][headline]
        if fh.add_bookmark(headline, url):
            self.bookmarks_menu.add_item(headline)
        else:
            return False

    def delete_bookmark(self):
        """Remove the selected bookmark from the list and bookmarks dictionary."""
        selection = self.bookmarks_menu.get()
        self.bookmarks_menu.remove_selected_item()
        del fh.bookmarks_dict[selection]

    def save_state(self):
        """Manually save all feed and bookmark data to JSON files."""
        if files.save_json(fh.feed_dict, 'feeds.json') and files.save_json(fh.bookmarks_dict, 'bookmarks.json'):
            self.root.show_message_popup('Success','Saved OK')
        else:
            self.show_error_message('Save Failed!')
            
    def show_error_message(self, msg: str) -> None:
        """Display an error popup with the given message."""
        self.root.show_error_popup('Error', msg)

    def get_menu_length(self, menu) -> int:
        """Return the number of items currently displayed in a given scroll menu."""
        try:
            return len(menu._view_items)
        except AttributeError:
            return 0

    def show_help(self):
        """Display the help text using Glow for Markdown formatting."""
        help_text = (
            "# PyCUI RSS Reader\n"
            "A lightweight terminal-based RSS reader built with **PyCUI**.\n"
            "It focuses on simplicity, responsiveness, and minimalism — a clean, no-fuss reading experience entirely in your terminal.\n"
            "## Keyboard Shortcuts\n"
            " **↑ / ↓**   : Navigate lists\n"
            " **Enter**   : Open feed/article/bookmark\n"
            " **T**       : Get an AI generated summary (TL;DR) for article/bookmark\n(Requires Free Goodle AI Studio API Key)\n"
            " **B**       : Bookmark article\n"
            " **D**       : Delete feed or bookmark\n"
            " **R**       : Refresh current feed\n"
            " **S**       : Save all feeds and bookmarks\n"
            " **X**       : Export selected file or bookmark as markdown\n"
            " **Q**       : Quit the app\n"
            " **H**       : Show this help\n\n"
            "**All feeds and bookmarks are automatically saved when you quit the application.**\n\n"
            "**Press 'Q' to exit help.**"
        )
        self.do_glow_text(help_text)

    def export_article_popup(self):
        """ Show a Save As dialog window. Set the file type to '.md' and pass the filename to save_md() """
        self.root.show_filedialog_popup(popup_type = 'saveas', callback = self.save_md, initial_dir = '.', ascii_icons = 'True', limit_extensions = ['.md'])

    def save_md(self, result):
        """ Take the supplied filename and grab the selected article URL from feed_nenu or bookmarks_menu,
        use fh.get_article() to return the Markdownified article text as a string,
        then pass the filename and article text to files.save.md() """
        filename = result
        if not filename.endswith('.md'): filename += '.md'
        if self.link_menu.is_selected(): url = self.current_feed['headlines'][self.link_menu.get()]
        if self.bookmarks_menu.is_selected(): url = fh.bookmarks_dict[self.bookmarks_menu.get()]
        article_text = fh.get_article(url)

        if files.save_md(article_text, filename ):
            self.root.show_message_popup('Success', f"Saved as: {filename}")
        else:
            self.show_error_message(f"Failed to save file: {filename}")

    def tl_dr(self):
        """
        Provides an AI generated summary of the highlighted article/bookmark.
        Check for the presence/validity of an API key and stores in .env
        Passes summarised article to Glow via do_glow_text.
        """
        if ai.api_key_ok():
            if self.link_menu.is_selected(): url = self.current_feed['headlines'][self.link_menu.get()]
            if self.bookmarks_menu.is_selected(): url = fh.bookmarks_dict[self.bookmarks_menu.get()]    

            article_text = fh.get_article(url)

            summary_text = ai.ask_gemini(article_text)
            if type(summary_text) == str: # If the article was not handled correctly, Gemini returns a JSON describing the problem.
                self.do_glow_text("# TL;DR Summary - Provide by Gemini-2.5-flash-lite\n" +  summary_text)
            else:
                if summary_text.code == 400: # Bad key supplied.
                    self.root.show_text_box_popup(summary_text.message, ai.save_api_key)
                else:
                    self.show_error_message(summary_text.message)
        else:
            self.root.show_text_box_popup('No API key found. Please paste your key below.', ai.save_api_key)
        
    def init_state(self):
        """Load saved feeds and bookmarks from JSON files and populate the interface."""
        fh.feed_dict = files.load_json('feeds.json') or {}
        fh.bookmarks_dict = files.load_json('bookmarks.json') or {}

        if fh.feed_dict:
            pub_list = [k for k in fh.feed_dict.keys() if k != 'refresh_interval']
            self.pub_menu.add_item_list(pub_list)
            self.bookmarks_menu.add_item_list(list(fh.bookmarks_dict.keys()))
            self.current_feed = fh.feed_dict[next(iter(fh.feed_dict))]
            self.show_articles()
        else:
            self.show_error_message('No feeds found. Try adding some now.')
        
            
if __name__ == "__main__":
    frame = py_cui.PyCUI(7, 8)
    frame.set_title(f"** PyCUI RSS Reader Version: {__version__} **")
    frame.toggle_unicode_borders()
    app = Interface(frame)
    try:
        app.init_state()
        frame.start()
    finally:
        app.save_state()
