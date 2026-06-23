import arcade


class MusicPlayer:
    def __init__(self):
        self.songs = {
            "another_him": arcade.load_sound("assets/audio/songs/ANOTHER_HIM.wav"),
            "faint_courage": arcade.load_sound("assets/audio/songs/faint-courage.wav"),
            "darkness_falls": arcade.load_sound("assets/audio/songs/darkness-falls.wav")
        }

        self.currently_playing_song_player = None

    def play_sound(self, sound_name: str = "", loop: bool = True, volume: float = 1.0, pitch: float = 1.0):
        """
        Stop the last playing song and play the requested song.
        :param sound_name: The name of the song to play in the self.songs dictionary.
        :param loop: A bool controlling whether to loop the song.
        :param volume: The volume of the song to be played.
        :param pitch: The pitch of the song to be played.
        :return:
        """
        # Stop any songs that are already playing.
        if self.currently_playing_song_player:
            arcade.stop_sound(self.currently_playing_song_player)

        if sound_name.lower() in self.songs:
            self.currently_playing_song_player = self.songs[sound_name].play()
            self.currently_playing_song_player.loop = loop
            self.currently_playing_song_player.volume = volume
            self.currently_playing_song_player.pitch = pitch

    def stop_sound(self):
        """
        Stop the currently playing song.
        :return: None
        """
        if self.currently_playing_song_player:
            arcade.stop_sound(self.currently_playing_song_player)

    def set_pitch(self, pitch: float):
        """
        Set the pitch of the currently playing song.
        :return: None
        """
        if self.currently_playing_song_player:
            self.currently_playing_song_player.pitch = pitch

    def set_volume(self, volume: float = 1.0):
        """
        Set the volume of the currently playing song.
        :return: None
        """
        if self.currently_playing_song_player:
            self.currently_playing_song_player.volume = volume
