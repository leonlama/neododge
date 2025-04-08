import arcade

def draw_pickup_texts(pickup_texts):
    for text, x, y, _ in pickup_texts:
        arcade.draw_text(text, x, y + 20, arcade.color.WHITE, 14, anchor_x="center")

def update_pickup_texts(pickup_texts, delta_time):
    """Update pickup text timers and positions."""
    updated_texts = []

    for text in pickup_texts:
        # Convert tuple to list if needed
        if isinstance(text, tuple):
            text = list(text)

        # Update timer
        text[3] -= delta_time

        # Move text upward
        text[2] += 1

        # Keep text if timer is still active
        if text[3] > 0:
            updated_texts.append(text)

    return updated_texts
