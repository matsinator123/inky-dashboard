from datetime import datetime, timedelta
from modules.calendar_data import get_calendar_events, next_daniel_day
from PIL import ImageDraw, ImageFont, Image

__all__ = ["draw_calendar_text", "draw_daniel_note"]

# Color constants (define here for self-containment, or import if COLORS is used elsewhere)
COLORS = {
    "black": (0, 0, 0),
    "red": (255, 0, 0),
}

def draw_calendar_text(draw: ImageDraw.ImageDraw, hand_font: ImageFont.ImageFont, start_x: int, start_y: int, max_width: int) -> int:
    """Draw today's and tomorrow's calendar events on the image."""
    events = get_calendar_events()
    today_str = str(datetime.now().date())
    tomorrow_str = str((datetime.now().date() + timedelta(days=1)))
    text_y = start_y
    line_count = 0
    max_lines = 5

    for date_str, day_events in events.items():
        if date_str == today_str:
            date_label = datetime.now().strftime("%d. %B %Y").lstrip("0")
            draw.text((start_x, text_y), f"{date_label}:", fill=COLORS["red"], font=hand_font)
        elif date_str == tomorrow_str:
            draw.text((start_x, text_y), "I morgen:", fill=COLORS["red"], font=hand_font)
        else:
            continue

        text_y += 38
        day_events.sort(key=lambda x: (x["time"] != "All Day", x["time"]))

        for event in day_events:
            if line_count == max_lines - 1:
                draw.text((start_x + 20, text_y), "flere hendelser...", fill=COLORS["red"], font=hand_font)
                return text_y + 28

            full_text = f"{event['time']} - {event['summary']}"
            words = full_text.split()
            line = ""
            lines = []
            for word in words:
                test = line + word + " "
                w = draw.textbbox((0, 0), test, font=hand_font)[2]
                if w <= max_width:
                    line = test
                else:
                    lines.append(line.strip())
                    line = word + " "
            lines.append(line.strip())

            for wrapped_line in lines:
                draw.text((start_x + 20, text_y), wrapped_line, fill=COLORS["black"], font=hand_font)
                text_y += 28
                line_count += 1

        text_y += 10

    return text_y

def draw_daniel_note(image: Image.Image, hand_font: ImageFont.ImageFont, x: int, y: int) -> None:
    """Draw a vertical note about the next Daniel event."""
    days = next_daniel_day()
    if days is None:
        return

    if days == 0:
        text = "Daniel\n i dag!\n <3"
    elif days == 1:
        text = "Daniel\n i morgen!"
    else:
        text = f"Daniel\nom {days} \ndager"

    note_width, note_height = 100, 1200
    text_img = Image.new("RGBA", (note_width, note_height), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_img)

    lines = text.split("\n")
    total_height = sum(
        text_draw.textbbox((0, 0), line, font=hand_font)[3] -
        text_draw.textbbox((0, 0), line, font=hand_font)[1]
        for line in lines
    )
    y_offset = (note_height - total_height) / 2

    for line in lines:
        bbox = text_draw.textbbox((0, 0), line, font=hand_font)
        text_draw.text(((note_width - (bbox[2] - bbox[0])) / 2, y_offset), line, font=hand_font, fill=COLORS["black"])
        y_offset += bbox[3] - bbox[1]

    rotated = text_img.rotate(22, expand=1)
    image.paste(rotated, (x, y), rotated)
