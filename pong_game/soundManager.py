import pygame
import os

class SoundManager:
    def __init__(self):
        """Initialize the sound system"""
        pygame.mixer.init()
        
        # Set default volume
        self.volume = 0.6
        
        # Load sound effects
        self.sounds = {}
        try:
            # Create sounds directory if it doesn't exist
            if not os.path.exists('sounds'):
                os.makedirs('sounds')
                
            # Define sound file paths
            sound_files = {
                'paddle_hit': 'sounds/paddle_hit.wav',
                'wall_hit': 'sounds/wall_hit.wav',
                'score': 'sounds/score.wav',
                'game_win': 'sounds/game_win.wav'
            }
            
            # Load each sound file
            for name, path in sound_files.items():
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.volume)
                else:
                    print(f"Warning: Sound file {path} not found")
                    
        except Exception as e:
            print(f"Error loading sounds: {e}")
            # Create placeholder sound (silent) if loading fails
            dummy_sound = pygame.mixer.Sound(buffer=bytes([0]*44))
            for name in ['paddle_hit', 'wall_hit', 'score', 'game_win']:
                self.sounds[name] = dummy_sound
    
    def play_sound(self, sound_name):
        """
        Play a sound by name
        
        Args:
            sound_name (str): Name of the sound to play
        """
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
            
    def set_volume(self, volume):
        """
        Set volume for all sounds
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.volume)