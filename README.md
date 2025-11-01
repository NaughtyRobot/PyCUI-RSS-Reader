# 📰 PyCUI RSS Reader

A lightweight terminal-based RSS reader built with PyCUI
 and Glow

It focuses on simplicity, responsiveness, and minimalism — a clean, no-fuss reading experience entirely in your terminal.

## ✨ Features

- Browse, add, and delete RSS feeds

- View article headlines and read full stories in Markdown via Glow

- Bookmark stories for later

- Refresh individual feeds on demand

- Persistent storage via JSON (feeds and bookmarks saved automatically)

- Compact, intuitive interface built with PyCUI scroll menus and text boxes

- Keyboard-driven navigation for fast, distraction-free reading

## 🎹 Key Bindings

**↑ / ↓** Navigate through lists
**Enter** Select feed / article / bookmark
**B**	Bookmark the selected article
**D**	Delete feed or bookmark
**R**	Refresh current feed
**S**	Save all feeds and bookmarks
**Q**	Quit the app
**H**	Help popup

**All feeds and bookmarks are automatically saved when you quit the application.**

## ⚙️ Requirements

Python 3.9+

Dependencies:

```
pip install py-cui feedparser trafilatura
```


Glow
 (for Markdown article rendering)

## ▶️ Usage

Run from the project root:
```
python rss_test_02.py
```

Add your first feed using the text box at the bottom-left and press Enter.
Feeds and bookmarks will persist between sessions.

## 📦 Notes

Articles are fetched on demand and rendered with Glow in Markdown.

Data (feeds and bookmarks) are stored as JSON in the project root.

On first launch, if no feeds exist, you’ll see a helpful prompt to add some.

## 🧭 Roadmap

- Configurable auto-refresh interval

- Optional OPML import/export

- Read/unread article tracking


## 🧡 Credits

Built by [Dave] using

PyCUI for the TUI

Glow for Markdown rendering

