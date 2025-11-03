__version__ = "1.0.0"

import curses
import os
import py_cui
import subprocess
import modules.feed_handler_pycui as fh
import modules.file_handler as files

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
        self.btn_save =  self.root.add_button('Save All', 6, 6, command = self.save_state)
        self.btn_refresh = self.root.add_button('Refresh Feed', 6, 7, command = self.refresh_feed)

        ## Key bindings ##
        self.root.add_key_command(py_cui.keys.KEY_H_LOWER, self.show_help)
        self.root.add_key_command(py_cui.keys.KEY_S_LOWER, self.save_state)
        self.root.add_key_command(py_cui.keys.KEY_R_LOWER, self.refresh_feed)

        self.new_feed_text.add_key_command(py_cui.keys.KEY_ENTER, self.add_feed)

        self.pub_menu.add_key_command(py_cui.keys.KEY_D_LOWER, self.delete_feed)
        self.pub_menu.add_key_command(py_cui.keys.KEY_ENTER, self.show_articles)
        self.pub_menu.add_key_command(py_cui.keys.KEY_R_LOWER, self.refresh_feed)


        self.link_menu.add_key_command(py_cui.keys.KEY_B_LOWER, self.add_bookmark)
        self.link_menu.add_key_command(py_cui.keys.KEY_ENTER, self.get_article)
        self.link_menu.add_key_command(py_cui.keys.KEY_R_LOWER, self.refresh_feed)
        self.link_menu.add_key_command(py_cui.keys.KEY_X_LOWER, self.export_article_popup)

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

    def show_articles(self, target: str = None):
        """Display the list of article headlines for the selected feed."""
        self.link_menu.clear()

        if not target:
            self.current_feed = fh.feed_dict[self.pub_menu.get()]

        self.link_menu.set_title(f"{self.pub_menu.get()} ({len(self.current_feed['headlines'].keys())})")
        headlines = [h for h in self.current_feed['headlines'].keys()]
        self.link_menu.add_item_list(headlines)
        self.feed_status.set_title(f"Feed last updated: {(self.current_feed['last_updated'])}")

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
        curses.endwin()
        subprocess.run(['glow','-p'], input = fh.get_article(url), text = True)
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
            " **B**       : Bookmark article\n"
            " **D**       : Delete feed or bookmark\n"
            " **R**       : Refresh current feed\n"
            " **S**       : Save all feeds and bookmarks\n"
            " **Q**       : Quit the app\n"
            " **H**       : Show this help\n\n"
            "**All feeds and bookmarks are automatically saved when you quit the application.**\n\n"
            "**Press 'Q' to exit help.**"
        )
        curses.endwin()
        subprocess.run(['glow','-p'], input = help_text, text = True)
        os.system('reset')

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
        
    def init_state(self):
        """Load saved feeds and bookmarks from JSON files and populate the interface."""
        fh.feed_dict = files.load_json('feeds.json') or {}
        fh.bookmarks_dict = files.load_json('bookmarks.json') or {}

        if fh.feed_dict:
            self.pub_menu.add_item_list(list(fh.feed_dict.keys()))
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
