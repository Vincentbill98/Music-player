import os
import pygame
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import random
from mutagen import File

# Define the extensions of music files to search for
music_extensions = ['.mp3', '.wav', '.ogg', '.flac']

# Initialize Pygame mixer
pygame.mixer.init()

# Global variables
playlist = []
current_song_index = -1
is_shuffling = False
is_repeating = False
current_song = None
metadata = None
volume = 1.0

def search_music_files(folder_path):
    music_files = []
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.endswith(ext) for ext in music_extensions):
                    music_files.append(os.path.join(root, file))
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while searching for files: {e}")
    return music_files

def get_metadata(file_path):
    try:
        audio = File(file_path)
        if audio:
            title = audio.get("title", ["Unknown"])[0]
            artist = audio.get("artist", ["Unknown"])[0]
            album = audio.get("album", ["Unknown"])[0]
            duration = audio.info.length if hasattr(audio.info, 'length') else "Unknown"
            return f"Title: {title}\nArtist: {artist}\nAlbum: {album}\nDuration: {duration:.2f} seconds"
        return "Metadata not available"
    except Exception as e:
        return f"Error retrieving metadata: {e}"

def play_next_song():
    global current_song_index, playlist, is_shuffling
    if not playlist:
        messagebox.showinfo("No Songs", "No songs available to play.")
        return

    if is_shuffling:
        current_song_index = random.randint(0, len(playlist) - 1)
    else:
        current_song_index = (current_song_index + 1) % len(playlist)

    if is_repeating and current_song_index == 0:
        play_music(playlist[current_song_index])
    else:
        file = playlist[current_song_index]
        play_music(file)

def play_music(file):
    if file:
        try:
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()
            current_song.set(f"Now playing: {os.path.basename(file)}")
            metadata.set(get_metadata(file))
            play_button.config(text="Pause")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while playing the file: {e}")

def toggle_play_pause():
    if pygame.mixer.music.get_busy():
        if pygame.mixer.music.get_pos() > 0:
            pygame.mixer.music.pause()
            play_button.config(text="Resume")
        else:
            pygame.mixer.music.unpause()
            play_button.config(text="Pause")
    else:
        selected_items = tree.selection()
        if selected_items:
            file = tree.item(selected_items[0], 'values')[0]
            play_music(file)
        else:
            messagebox.showinfo("No Selection", "Please select a song to play.")

def stop_music():
    pygame.mixer.music.stop()
    play_button.config(text="Play")
    current_song.set("Music Stopped")
    metadata.set("")

def update_volume(val):
    global volume
    volume = float(val) / 100
    pygame.mixer.music.set_volume(volume)

def open_folder_and_populate_tree():
    folder_path = filedialog.askdirectory()
    if folder_path:
        try:
            global playlist
            files = search_music_files(folder_path)
            if files:
                # Filter out duplicates
                unique_files = list(set(files))
                playlist = unique_files
                populate_treeview(playlist)
                current_song.set("")
                metadata.set("")
                play_button.config(text="Play")
                stop_music()
            else:
                messagebox.showinfo("No Files", "No music files found in the selected folder.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

def populate_treeview(files):
    for i in tree.get_children():
        tree.delete(i)
    added_files = set()  # To track already added files
    for file in files:
        if file not in added_files:
            tree.insert('', 'end', text=os.path.basename(file), values=(file,))
            added_files.add(file)

def play_selected_songs():
    global playlist, current_song_index
    selected_items = tree.selection()
    if selected_items:
        playlist = [tree.item(item, 'values')[0] for item in selected_items]
        current_song_index = -1
        play_next_song()
    else:
        messagebox.showinfo("No Selection", "Please select one or more songs from the list.")

def toggle_shuffle():
    global is_shuffling
    is_shuffling = not is_shuffling
    shuffle_button.config(text="Shuffle On" if is_shuffling else "Shuffle Off")

def toggle_repeat():
    global is_repeating
    is_repeating = not is_repeating
    repeat_button.config(text="Repeat On" if is_repeating else "Repeat Off")

def search_songs():
    query = search_entry.get().lower()
    for item in tree.get_children():
        song_name = tree.item(item, 'text').lower()
        if query in song_name:
            tree.item(item, tags=('search_match',))
        else:
            tree.item(item, tags=())
    tree.tag_configure('search_match', background='#4B6A9F')

# Initialize Tkinter window
root = tk.Tk()
root.title("Music Player")
root.geometry("800x600")

# Define Tkinter variables
current_song = tk.StringVar()
metadata = tk.StringVar()
volume = 1.0

# Configure the main frame
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Apply custom style to the Treeview
style = ttk.Style()
style.configure('Treeview',
                background='#2E3B4E',
                foreground='#FFFFFF',
                rowheight=30,
                fieldbackground='#2E3B4E')
style.configure('Treeview.Heading',
                background='#1E2A38',
                foreground='#FFFFFF',
                font=('Arial', 12, 'bold'))
style.map('Treeview',
          background=[('selected', '#3D4F6C')])

# Left side widgets
left_frame = tk.Frame(main_frame)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

open_folder_button = tk.Button(left_frame, text="Open Folder and Populate Songs", command=open_folder_and_populate_tree, font=("Arial", 12))
open_folder_button.pack(pady=5)

play_button = tk.Button(left_frame, text="Play", command=toggle_play_pause, font=("Arial", 12))
play_button.pack(pady=5)

stop_button = tk.Button(left_frame, text="Stop Music", command=stop_music, font=("Arial", 12))
stop_button.pack(pady=5)

shuffle_button = tk.Button(left_frame, text="Shuffle Off", command=toggle_shuffle, font=("Arial", 12))
shuffle_button.pack(pady=5)

repeat_button = tk.Button(left_frame, text="Repeat Off", command=toggle_repeat, font=("Arial", 12))
repeat_button.pack(pady=5)

current_song_label = tk.Label(left_frame, textvariable=current_song, font=("Arial", 12))
current_song_label.pack(pady=10)

metadata_label = tk.Label(left_frame, textvariable=metadata, font=("Arial", 10), justify=tk.LEFT)
metadata_label.pack(pady=10)

volume_label = tk.Label(left_frame, text="Volume", font=("Arial", 12))
volume_label.pack(pady=5)

volume_slider = tk.Scale(left_frame, from_=0, to=100, orient=tk.HORIZONTAL, command=update_volume, length=300)
volume_slider.set(100)  # Set default volume to 100%
volume_slider.pack(pady=10)

search_label = tk.Label(left_frame, text="Search:", font=("Arial", 12))
search_label.pack(pady=5)

search_entry = tk.Entry(left_frame, font=("Arial", 12))
search_entry.pack(pady=5)

search_button = tk.Button(left_frame, text="Search", command=search_songs, font=("Arial", 12))
search_button.pack(pady=5)

# Right side widgets
tree_frame = tk.Frame(main_frame)
tree_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

tree_scroll = tk.Scrollbar(tree_frame)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree = ttk.Treeview(tree_frame, columns=("File Path"), show="tree", yscrollcommand=tree_scroll.set, selectmode="extended")
tree.pack(pady=10, fill=tk.BOTH, expand=True)

tree_scroll.config(command=tree.yview)

# Run the Tkinter main loop
root.mainloop()
