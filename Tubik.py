import customtkinter as ctk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import json
import threading

SETTINGS_FILE = "settings.json"

# Define themes
THEMES = {
    "Light": {"fg": "black", "bg": "white", "button_fg": "black", "button_bg": "lightgrey"},
    "Dark": {"fg": "white", "bg": "#333333", "button_fg": "white", "button_bg": "#555555"},
    "Tokyo Night": {"fg": "#7aa2f7", "bg": "#1a1b26", "button_fg": "#f7768e", "button_bg": "#1a1b26"},
    "Dracula": {"fg": "#bd93f9", "bg": "#282a36", "button_fg": "#f8f8f2", "button_bg": "#44475a"},
    "Solarized": {"fg": "#586e75", "bg": "#fdf6e3", "button_fg": "#073642", "button_bg": "#eee8d5"},
    "Monokai": {"fg": "#f92672", "bg": "#272822", "button_fg": "#a6e22e", "button_bg": "#49483e"},
    "Oceanic": {"fg": "#6699cc", "bg": "#1b2b34", "button_fg": "#ec5f67", "button_bg": "#343d46"},
    "Material Dark": {"fg": "#ffffff", "bg": "#121212", "button_fg": "#bb86fc", "button_bg": "#333333"},
    "Nord": {"fg": "#d8dee9", "bg": "#2e3440", "button_fg": "#88c0d0", "button_bg": "#4c566a"},
    "Gruvbox": {"fg": "#ebdbb2", "bg": "#282828", "button_fg": "#fabd2f", "button_bg": "#3c3836"},
    "Tomorrow Night": {"fg": "#c5c8c6", "bg": "#1d1f21", "button_fg": "#81a2be", "button_bg": "#373b41"},
}

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Tubik - YouTube Downloader")
        self.geometry("600x500")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.selected_theme = self.load_theme()

        # Heading
        self.heading_label = ctk.CTkLabel(self, text="Tubik - YouTube Downloader", font=("Arial", 24, "bold"))
        self.heading_label.pack(pady=10)

        # URL Entry
        self.url_label = ctk.CTkLabel(self, text="Enter YouTube URL:", font=("Arial", 14))
        self.url_label.pack(pady=10)

        self.url_entry = ctk.CTkEntry(self, placeholder_text="Paste the YouTube video URL here...", width=400)
        self.url_entry.pack(pady=10)

        # Download Button
        self.download_button = ctk.CTkButton(self, text="Download", command=self.download_video, width=200, height=40)
        self.download_button.pack(pady=20)

        # Theme Selection
        self.theme_label = ctk.CTkLabel(self, text="Select Theme:", font=("Arial", 14))
        self.theme_label.pack(pady=10)

        self.theme_menu = ctk.CTkOptionMenu(self, values=list(THEMES.keys()), command=self.change_theme)
        self.theme_menu.pack(pady=10)
        self.theme_menu.set(self.selected_theme)  # Load saved theme

        # Download Format Selection
        self.format_label = ctk.CTkLabel(self, text="Select Download Format:", font=("Arial", 14))
        self.format_label.pack(pady=10)

        self.format_menu = ctk.CTkOptionMenu(self, values=["Video (MP4)", "Audio (MP3)"], command=self.select_format)
        self.format_menu.pack(pady=10)

        # Status Label (Alternative to progress bar)
        self.status_label = ctk.CTkLabel(self, text="Ready to download", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.selected_format = "Video (MP4)"  # Default format
        self.change_theme(self.selected_theme)  # Apply saved theme

    def load_theme(self):
        """Load the saved theme from the settings file."""
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                settings = json.load(f)
                return settings.get("theme", "Light")
        return "Light"

    def save_theme(self):
        """Save the selected theme to the settings file."""
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"theme": self.selected_theme}, f)

    def change_theme(self, selected_theme):
        """Apply the selected theme."""
        self.selected_theme = selected_theme
        self.save_theme()
        theme = THEMES[selected_theme]
        self.configure(fg_color=theme["bg"])
        self.heading_label.configure(text_color=theme["fg"])
        self.url_label.configure(text_color=theme["fg"])
        self.theme_label.configure(text_color=theme["fg"])
        self.download_button.configure(fg_color=theme["button_fg"])
        self.status_label.configure(text_color=theme["fg"])

    def select_format(self, selected_format):
        """Update selected download format."""
        self.selected_format = selected_format

    def download_video(self):
        """Download the video or audio using yt-dlp in a separate thread."""
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            return

        save_path = filedialog.askdirectory(title="Select Save Folder")
        if not save_path:
            messagebox.showerror("Error", "Please select a save folder")
            return

        if self.selected_format == "Video (MP4)":
            options = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': f"{save_path}/%(title)s.%(ext)s",  # Ensure output is .mp4
                'merge_output_format': 'mp4',  # Force mp4 format
            }
        elif self.selected_format == "Audio (MP3)":
            options = {
                'format': 'bestaudio/best',
                'outtmpl': f"{save_path}/%(title)s.%(ext)s",  # Ensure audio file is in MP3 format
                'extractaudio': True,
                'audioformat': 'mp3',  # Convert to mp3
            }

        # Update status
        self.status_label.configure(text="Starting download...")

        # Start download in a separate thread to avoid blocking the main GUI thread
        download_thread = threading.Thread(target=self.start_download, args=(options, url))
        download_thread.start()

    def start_download(self, options, url):
        """Run the yt-dlp download in a separate thread."""
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                self.status_label.configure(text="Downloading...")
                ydl.download([url])
            self.status_label.configure(text="Download completed successfully!")
        except Exception as e:
            self.status_label.configure(text="Download failed!")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()
