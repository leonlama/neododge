import arcade

class PickupText:
    def __init__(self, text, x, y, color=arcade.color.WHITE, duration=1.0):
        self.alpha = 255
        self.duration = duration
        self.timer = 0.0
        self.color = color
        self.x = x
        self.y = y
        
        self.text = arcade.Text(
            text,
            x,
            y,
            color,
            font_size=15,
            anchor_x="center",
            anchor_y="center",
            font_name="Kenney Pixel"
        )

    def update(self, delta_time):
        self.timer += delta_time
        if self.timer >= self.duration:
            self.alpha = 0
        else:
            self.alpha = int(255 * (1 - self.timer / self.duration))
            self.y += 30 * delta_time  # float upward
            self.text.y = self.y  # Update text position

    def draw(self):
        # Update the color with current alpha
        self.text.color = (*self.color[:3], self.alpha)
        self.text.draw()