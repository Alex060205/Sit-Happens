import os
import winsound
import tkinter as tk
from tkinter import filedialog


class AlarmManager:
    def __init__(self, default_sound: str = "coconut-mall.wav", loop: bool = False):
        """
        Generalizable audio alert manager for Posture Guard.

        Args:
            default_sound: Filename or full path to the default .wav alert file.
            loop: If True, loops the alert continuously until stop() is called.
        """
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.loop = loop
        self.is_playing = False
        self.current_sound_path = None

        # Set initial sound if it exists
        if default_sound:
            self.set_sound(default_sound)

    def set_sound(self, file_path: str) -> bool:
        """
        Sets the active alert sound from a filename (in project dir) or full path.
        Returns True if the file exists and is valid, False otherwise.
        """
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.base_dir, file_path)

        if os.path.exists(file_path) and file_path.lower().endswith(".wav"):
            self.stop()
            self.current_sound_path = file_path
            return True
        return False

    def select_custom_sound(self) -> str | None:
        """
        Opens a native Windows file picker so the user can choose any .wav file.
        Returns the selected file path, or None if cancelled.
        """
        root = tk.Tk()
        root.withdraw()  # Hide the blank Tkinter root window
        root.attributes("-topmost", True)  # Bring file dialog to front

        selected_path = filedialog.askopenfilename(
            title="Select Alert Sound (.wav)",
            filetypes=[("WAV Audio Files", "*.wav")],
        )
        root.destroy()

        if selected_path and self.set_sound(selected_path):
            return selected_path
        return None


    def play(self):
        """Plays the selected .wav file asynchronously without freezing the UI."""
        if self.is_playing:
            return

        if self.current_sound_path and os.path.exists(self.current_sound_path):
            flags = winsound.SND_FILENAME | winsound.SND_ASYNC
            if self.loop:
                flags |= winsound.SND_LOOP
            winsound.PlaySound(self.current_sound_path, flags)
            self.is_playing = True


    def stop(self):
        """Immediately stops any currently playing alert sound."""
        if self.is_playing:
            winsound.PlaySound(None, winsound.SND_PURGE)
            self.is_playing = False