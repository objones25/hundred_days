class Theme:
    def __init__(self, name: str, snake_color, food_color, bg_color):
        self.name = name
        self.snake_color = snake_color
        self.food_color = food_color
        self.bg_color = bg_color

class ThemeManager:
    @staticmethod
    def get_themes():
        return {
            "classic": Theme("Classic", (0, 255, 0), (255, 0, 0), (0, 0, 0)),
            "desert": Theme("Desert", (194, 178, 128), (255, 140, 0), (242, 210, 169)),
            "forest": Theme("Forest", (34, 139, 34), (139, 69, 19), (0, 100, 0)),
            "neon": Theme("Neon", (0, 255, 255), (255, 0, 255), (25, 25, 25))
        }