from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.core.text import Label as CoreLabel
import random
import time


class TouchApp(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_tap_time = 0
        self.tap_delay = 0.3  # 300 ms
        self.long_press_time = 1.0  # 1 second
        self.screen_color = [1, 1, 1, 0.5]  # Default translucent white
        self.timer_started = False
        self.start_time = 0
        self.flash_timer_event = None
        self.circles = []
        # 3D text "Mohit" at the bottom center
        self.mohit_label = CoreLabel(
            text="Mohit", font_size=100, bold=True  # Set bold and large font size
        )
        self.mohit_label.refresh()
        self.mohit_texture = self.mohit_label.texture

        # Add 3D effect with shadows
        with self.canvas:
            self.mohit_shadow_color = Color(0.2, 0.2, 0.2, 1)  # Dark shadow
            for offset in range(5, 0, -1):  # Draw shadow with offsets
                Rectangle(
                    texture=self.mohit_texture,
                    size=self.mohit_texture.size,
                    pos=(
                        (self.width - self.mohit_texture.width) / 2 + offset,
                        self.height * 0.05 + offset,
                    ),
                )

            self.mohit_main_color = Color(1, 1, 1, 1)  # Bright white main text
            self.mohit_text_rect = Rectangle(
                texture=self.mohit_texture,
                size=self.mohit_texture.size,
                pos=(
                    (self.width - self.mohit_texture.width) / 2,
                    self.height * 0.05,
                ),
            )



        with self.canvas:
            # Background color
            self.bg_color = Color(*self.screen_color)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)

            # Timer text
            self.timer_label = CoreLabel(
                text="00:00:00.000",  # Default timer text with milliseconds
                font_size=120,        # Increased font size
                bold=True             # Make it bold
            )
            self.timer_label.refresh()
            self.timer_texture = self.timer_label.texture
            self.timer_color = Color(0, 0, 0, 1)
            self.timer_rect = Rectangle(texture=self.timer_texture, size=self.timer_texture.size)


        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def update_canvas(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos
        # Update "Mohit" text position
        self.mohit_text_rect.pos = (
            (self.width - self.mohit_texture.width) / 2,
            self.height * 0.05,
        )


        # Update timer position (top half of the screen)
        self.timer_rect.pos = (self.width / 2 - self.timer_texture.width / 2, self.height * 0.75)

    def on_touch_down(self, touch):
        current_time = time.time()
        time_since_last_tap = current_time - self.last_tap_time

        # Detect long press
        Clock.schedule_once(self.long_press_action, self.long_press_time)

        # Start the timer on the first tap
        if not self.timer_started:
            self.start_time = time.time()
            self.timer_started = True
            Clock.schedule_interval(self.update_timer, 0.1)
            self.flash_timer_event = Clock.schedule_interval(self.flash_screen, 2)

        # If time since the last tap is less than 100 ms, do nothing
        if time_since_last_tap < 0.1:
            return

        # If time since the last tap is greater than 300 ms, change screen color
        if time_since_last_tap >= self.tap_delay:
            self.change_screen_color()

        # Draw a circle with the negative color
        with self.canvas:
            negative_color = [1 - c for c in self.screen_color[:3]] + [1]
            Color(*negative_color)
            circle = Ellipse(pos=(touch.x - 10, touch.y - 10), size=(20, 20))
            self.circles.append({"circle": circle, "time": time.time(), "size_increase": 0})

        self.last_tap_time = current_time

    def on_touch_up(self, touch):
        # Cancel long press detection if touch is released quickly
        Clock.unschedule(self.long_press_action)

    def change_screen_color(self):
        # Generate a random color
        self.screen_color = [random.random(), random.random(), random.random(), 0.5]
        self.bg_color.rgba = self.screen_color

    def long_press_action(self, dt):
        # Flash the screen white for 10 ms
        self.flash_screen(duration=0.01, color=[1, 1, 1, 1])

# Calculate hours, minutes, seconds, and milliseconds
# Update the timer label to include the formatted time with milliseconds

    def update_timer(self, dt):
        if not self.timer_started:
            return
        elapsed_time = time.time() - self.start_time
        hours, rem = divmod(int(elapsed_time), 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = int((elapsed_time - int(elapsed_time)) * 1000)  # Get milliseconds
        self.timer_label.text = f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"  # Include milliseconds
        self.timer_label.refresh()
        self.timer_texture = self.timer_label.texture
        self.timer_rect.texture = self.timer_texture
        self.timer_rect.size = self.timer_texture.size
        self.update_canvas()

    # Handle circles
        self.update_circles()


        
    def update_circles(self):
        current_time = time.time()
        for circle_info in self.circles[:]:
            circle = circle_info["circle"]
            creation_time = circle_info["time"]
            elapsed_time = current_time - creation_time

            # Increase circle size every 2 seconds
            if elapsed_time >= 2 and circle_info["size_increase"] == 0:
                circle.size = (circle.size[0] + 20, circle.size[1] + 20)
                circle_info["size_increase"] = 1

            # Remove circle after 2 seconds
            if elapsed_time >= 2:
                self.canvas.remove(circle)
                self.circles.remove(circle_info)


# Determine the flash color and duration
# Yellow flash lasts 10 ms; white flash lasts 20 ms
# Restore the original background color after the flash duration

    def flash_screen(self, dt=None, duration=0.01, color=None):
        if not color:
            if self.screen_color[:3] == [1, 1, 0]:  # If screen is yellow
                color = [1, 0, 1, 1]  # Flash pink
            else:
                color = [1, 1, 0, 1]  # Flash yellow
                duration = 0.01  # Yellow flash lasts 10 ms
        elif color == [1, 1, 1, 1]:  # If white screen
            duration = 0.02  # White flash lasts 20 ms

        self.bg_color.rgba = color
        Clock.schedule_once(lambda dt: setattr(self.bg_color, 'rgba', self.screen_color), duration)



class COLO(App):
    def build(self):
        return TouchApp()


if __name__ == '__main__':
    COLO().run()
