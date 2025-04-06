
import arcade

def draw_pickup_texts(pickup_texts):
    for text, x, y, _ in pickup_texts:
        arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

def update_pickup_texts(pickup_texts, delta_time):
    for t in pickup_texts:
        t[3] -= delta_time
    return [t for t in pickup_texts if t[3] > 0]