from pathlib import Path

import pygame


class MusicPlayer:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.width = 900
        self.height = 500
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Music Player with Keyboard Controller")

        self.clock = pygame.time.Clock()
        self.running = True

        self.bg_color = (245, 245, 245)
        self.black = (20, 20, 20)
        self.green = (40, 160, 90)
        self.red = (200, 60, 60)
        self.blue = (60, 110, 220)

        self.title_font = pygame.font.SysFont("arial", 34)
        self.text_font = pygame.font.SysFont("arial", 26)
        self.small_font = pygame.font.SysFont("arial", 22)

        self.base_path = Path(__file__).resolve().parent
        self.music_dir = self.base_path / "music"

        self.tracks = self.load_tracks()
        self.current_index = 0
        self.is_playing = False
        self.track_start_ticks = 0

    def load_tracks(self):
        """
        Loads all .mp3 and .wav files from the music folder.
        """
        tracks = []

        if not self.music_dir.exists():
            self.music_dir.mkdir(parents=True, exist_ok=True)

        for path in sorted(self.music_dir.iterdir()):
            if path.suffix.lower() in [".mp3", ".wav"]:
                tracks.append(path)

        return tracks

    def get_current_track(self):
        if not self.tracks:
            return None
        return self.tracks[self.current_index]

    def play(self):
        current_track = self.get_current_track()
        if current_track is None:
            return

        pygame.mixer.music.load(str(current_track))
        pygame.mixer.music.play()
        self.is_playing = True
        self.track_start_ticks = pygame.time.get_ticks()

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        if not self.tracks:
            return
        self.current_index = (self.current_index + 1) % len(self.tracks)
        if self.is_playing:
            self.play()

    def previous_track(self):
        if not self.tracks:
            return
        self.current_index = (self.current_index - 1) % len(self.tracks)
        if self.is_playing:
            self.play()

    def get_elapsed_seconds(self):
        if not self.is_playing:
            return 0
        return (pygame.time.get_ticks() - self.track_start_ticks) // 1000

    def format_time(self, seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02}:{remaining_seconds:02}"

    def draw(self):
        self.screen.fill(self.bg_color)

        title = self.title_font.render("Music Player", True, self.black)
        self.screen.blit(title, (30, 20))

        controls = [
            "Keyboard controls:",
            "P = Play",
            "S = Stop",
            "N = Next track",
            "B = Previous track",
            "Q = Quit",
        ]

        y = 90
        for line in controls:
            rendered = self.text_font.render(line, True, self.black)
            self.screen.blit(rendered, (30, y))
            y += 35

        if self.tracks:
            current = self.get_current_track()
            current_name = current.name
        else:
            current_name = "No audio files in /music folder"

        track_text = self.text_font.render(f"Current track: {current_name}", True, self.blue)
        self.screen.blit(track_text, (30, 320))

        status = "Playing" if self.is_playing else "Stopped"
        color = self.green if self.is_playing else self.red
        status_text = self.text_font.render(f"Status: {status}", True, color)
        self.screen.blit(status_text, (30, 360))

        elapsed = self.format_time(self.get_elapsed_seconds())
        elapsed_text = self.text_font.render(f"Playback position: {elapsed}", True, self.black)
        self.screen.blit(elapsed_text, (30, 400))

        playlist_title = self.text_font.render("Playlist:", True, self.black)
        self.screen.blit(playlist_title, (520, 90))

        if self.tracks:
            y = 130
            for index, track in enumerate(self.tracks):
                prefix = "-> " if index == self.current_index else "   "
                line = self.small_font.render(prefix + track.name, True, self.black)
                self.screen.blit(line, (520, y))
                y += 30
        else:
            empty_text = self.small_font.render("Add .mp3 or .wav files to the music folder.", True, self.red)
            self.screen.blit(empty_text, (520, 130))

        pygame.display.flip()

    def handle_keydown(self, key):
        if key == pygame.K_p:
            self.play()
        elif key == pygame.K_s:
            self.stop()
        elif key == pygame.K_n:
            self.next_track()
        elif key == pygame.K_b:
            self.previous_track()
        elif key == pygame.K_q:
            self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(60)

        pygame.mixer.music.stop()
        pygame.quit()