from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen


# ─── HOME SCREEN ───────────────────────────────────────────
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(
            text='🐟 FishNav',
            font_size='32sp',
            bold=True,
            size_hint=(1, 0.2)
        ))

        buttons = [
            ('🗺️  Map',           'green',  'map'),
            ('📍  My Spots',      'blue',   'spots'),
            ('🌤️  Weather',       'orange', 'weather'),
            ('⬇️  Download Maps', 'purple', 'download'),
        ]

        for label, color, screen_name in buttons:
            btn = Button(
                text=label,
                font_size='22sp',
                size_hint=(1, 0.2),
                background_color=self.get_color(color)
            )
            btn.screen_name = screen_name
            btn.bind(on_press=self.go_to_screen)
            layout.add_widget(btn)

        self.add_widget(layout)

    def get_color(self, name):
        colors = {
            'green':  (0.1, 0.7, 0.3, 1),
            'blue':   (0.1, 0.4, 0.8, 1),
            'orange': (0.9, 0.5, 0.1, 1),
            'purple': (0.5, 0.1, 0.8, 1),
        }
        return colors.get(name, (0.5, 0.5, 0.5, 1))

    def go_to_screen(self, btn):
        self.manager.current = btn.screen_name


# ─── MAP SCREEN ────────────────────────────────────────────
class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Top bar
        top_bar = BoxLayout(size_hint=(1, 0.08), spacing=10)
        back_btn = Button(
            text='⬅ Back',
            size_hint=(0.3, 1),
            background_color=(0.2, 0.2, 0.2, 1)
        )
        back_btn.bind(on_press=self.go_back)
        title = Label(text='🗺️  Map', font_size='20sp', bold=True)
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title)
        layout.add_widget(top_bar)

        # Map placeholder (real map coming next step)
        self.map_area = Label(
            text='📡 Map loads here\n\n(GPS: searching...)',
            font_size='18sp',
            halign='center',
            size_hint=(1, 0.75),
            color=(0.2, 0.8, 0.4, 1)
        )
        layout.add_widget(self.map_area)

        # Bottom action buttons
        bottom_bar = BoxLayout(size_hint=(1, 0.12), spacing=10)
        save_btn = Button(
            text='📍 Save Spot',
            font_size='18sp',
            background_color=(0.1, 0.6, 0.9, 1)
        )
        track_btn = Button(
            text='🔴 Track Route',
            font_size='18sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        save_btn.bind(on_press=self.save_spot)
        track_btn.bind(on_press=self.toggle_tracking)
        bottom_bar.add_widget(save_btn)
        bottom_bar.add_widget(track_btn)
        layout.add_widget(bottom_bar)

        self.add_widget(layout)
        self.tracking = False

    def go_back(self, btn):
        self.manager.current = 'home'

    def save_spot(self, btn):
        self.map_area.text = '📍 Spot Saved!\n\nLat: 12.9716\nLon: 74.8631'

    def toggle_tracking(self, btn):
        self.tracking = not self.tracking
        if self.tracking:
            self.map_area.text = '🔴 Tracking route...\n\nMove the boat!'
        else:
            self.map_area.text = '⏹️ Route stopped\n\nRoute saved!'


# ─── PLACEHOLDER SCREENS ───────────────────────────────────
class SpotsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text='📍 My Spots\n\nComing soon!',
                                font_size='22sp', halign='center'))
        back_btn = Button(text='⬅ Back', size_hint=(1, 0.15),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

class WeatherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text='🌤️ Weather\n\nComing soon!',
                                font_size='22sp', halign='center'))
        back_btn = Button(text='⬅ Back', size_hint=(1, 0.15),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

class DownloadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text='⬇️ Download Maps\n\nComing soon!',
                                font_size='22sp', halign='center'))
        back_btn = Button(text='⬅ Back', size_hint=(1, 0.15),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        self.add_widget(layout)


# ─── APP ENTRY POINT ───────────────────────────────────────
class FishNavApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MapScreen(name='map'))
        sm.add_widget(SpotsScreen(name='spots'))
        sm.add_widget(WeatherScreen(name='weather'))
        sm.add_widget(DownloadScreen(name='download'))
        return sm


if __name__ == '__main__':
    FishNavApp().run()