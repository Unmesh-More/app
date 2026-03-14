from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from plyer import gps
import sqlite3
import os
from weather import fetch_weather_by_coords, init_weather_cache, wind_advice
from kivy.uix.textinput import TextInput


# ─── DATABASE SETUP ────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), 'fishnav.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS spots (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT,
            lat     REAL,
            lon     REAL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS routes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            lat      REAL,
            lon      REAL,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_spot_to_db(name, lat, lon):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO spots (name, lat, lon) VALUES (?, ?, ?)',
              (name, lat, lon))
    conn.commit()
    conn.close()

def get_all_spots():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name, lat, lon, saved_at FROM spots ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def save_route_point(lat, lon):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO routes (lat, lon) VALUES (?, ?)', (lat, lon))
    conn.commit()
    conn.close()


# ─── GPS MANAGER ───────────────────────────────────────────
class GPSManager:
    def __init__(self):
        self.lat = None
        self.lon = None
        self.status = 'Searching GPS...'
        self.on_location_callback = None

    def start(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
            gps.start(minTime=1000, minDistance=1)
        except Exception:
            # On Windows/PC, GPS is not available — use simulation
            self.status = 'Simulated GPS (PC mode)'
            self.lat = 12.9716   # Mangalore coast default
            self.lon = 74.8631
            Clock.schedule_interval(self.simulate_gps, 3)

    def simulate_gps(self, dt):
        # Slightly move position to simulate boat movement
        if self.lat:
            self.lat += 0.0001
            self.lon += 0.0001
            self.status = f'Simulated GPS active'
            if self.on_location_callback:
                self.on_location_callback(self.lat, self.lon)

    def on_location(self, **kwargs):
        self.lat = kwargs.get('lat')
        self.lon = kwargs.get('lon')
        self.status = 'GPS Fixed ✅'
        if self.on_location_callback:
            self.on_location_callback(self.lat, self.lon)

    def on_status(self, stype, status):
        self.status = status

    def stop(self):
        try:
            gps.stop()
        except Exception:
            pass


gps_manager = GPSManager()


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
        self.tracking = False
        self.spot_count = 0

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Top bar
        top_bar = BoxLayout(size_hint=(1, 0.08), spacing=10)
        back_btn = Button(text='⬅ Back', size_hint=(0.3, 1),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=self.go_back)
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='🗺️  Map', font_size='20sp', bold=True))
        layout.add_widget(top_bar)

        # GPS status bar
        self.gps_label = Label(
            text='📡 ' + gps_manager.status,
            font_size='15sp',
            size_hint=(1, 0.07),
            color=(0.2, 0.9, 0.4, 1)
        )
        layout.add_widget(self.gps_label)

        # Map display area
        self.map_area = Label(
            text='Waiting for GPS...',
            font_size='17sp',
            halign='center',
            valign='middle',
            size_hint=(1, 0.70)
        )
        layout.add_widget(self.map_area)

        # Bottom buttons
        bottom_bar = BoxLayout(size_hint=(1, 0.12), spacing=10)
        self.save_btn = Button(
            text='📍 Save Spot',
            font_size='18sp',
            background_color=(0.1, 0.6, 0.9, 1)
        )
        self.track_btn = Button(
            text='🔴 Start Track',
            font_size='18sp',
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.save_btn.bind(on_press=self.save_spot)
        self.track_btn.bind(on_press=self.toggle_tracking)
        bottom_bar.add_widget(self.save_btn)
        bottom_bar.add_widget(self.track_btn)
        layout.add_widget(bottom_bar)

        self.add_widget(layout)

        # Start GPS and update UI
        gps_manager.on_location_callback = self.update_gps_display
        gps_manager.start()
        Clock.schedule_interval(self.refresh_gps_status, 2)

    def refresh_gps_status(self, dt):
        self.gps_label.text = '📡 ' + gps_manager.status
        if gps_manager.lat:
            self.update_gps_display(gps_manager.lat, gps_manager.lon)

    def update_gps_display(self, lat, lon):
        self.map_area.text = (
            f'📍 Current Position\n\n'
            f'Latitude:   {lat:.6f}°\n'
            f'Longitude:  {lon:.6f}°\n\n'
            f'Spots saved this session: {self.spot_count}'
        )

    def save_spot(self, btn):
        if gps_manager.lat:
            self.spot_count += 1
            name = f'Spot {self.spot_count}'
            save_spot_to_db(name, gps_manager.lat, gps_manager.lon)
            self.map_area.text = (
                f'✅ {name} Saved!\n\n'
                f'Lat: {gps_manager.lat:.6f}°\n'
                f'Lon: {gps_manager.lon:.6f}°\n\n'
                f'Total spots: {self.spot_count}'
            )
        else:
            self.map_area.text = '⚠️ No GPS signal yet!\nPlease wait...'

    def toggle_tracking(self, btn):
        self.tracking = not self.tracking
        if self.tracking:
            self.track_btn.text = '⏹️ Stop Track'
            self.track_btn.background_color = (0.3, 0.3, 0.3, 1)
            Clock.schedule_interval(self.record_route_point, 5)
        else:
            self.track_btn.text = '🔴 Start Track'
            self.track_btn.background_color = (0.8, 0.2, 0.2, 1)
            Clock.unschedule(self.record_route_point)
            self.map_area.text = '⏹️ Route saved!\n\nCheck My Spots screen.'

    def record_route_point(self, dt):
        if gps_manager.lat:
            save_route_point(gps_manager.lat, gps_manager.lon)

    def go_back(self, btn):
        self.manager.current = 'home'


# ─── MY SPOTS SCREEN ───────────────────────────────────────
class SpotsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Top bar
        top_bar = BoxLayout(size_hint=(1, 0.08), spacing=10)
        back_btn = Button(text='⬅ Back', size_hint=(0.3, 1),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='📍 My Spots', font_size='20sp', bold=True))
        self.layout.add_widget(top_bar)

        # Scrollable spots list
        self.scroll = ScrollView(size_hint=(1, 0.92))
        self.spots_grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        self.spots_grid.bind(minimum_height=self.spots_grid.setter('height'))
        self.scroll.add_widget(self.spots_grid)
        self.layout.add_widget(self.scroll)

        self.add_widget(self.layout)

    def on_enter(self):
        # Refresh spots every time screen is opened
        self.spots_grid.clear_widgets()
        spots = get_all_spots()
        if not spots:
            self.spots_grid.add_widget(Label(
                text='No spots saved yet!\nGo to Map and save some. 🐟',
                font_size='18sp',
                halign='center',
                size_hint_y=None,
                height=100
            ))
        for name, lat, lon, saved_at in spots:
            text = f'📍 {name}\nLat: {lat:.5f}  Lon: {lon:.5f}\n🕒 {saved_at[:16]}'
            lbl = Button(
                text=text,
                font_size='15sp',
                halign='left',
                size_hint_y=None,
                height=90,
                background_color=(0.1, 0.3, 0.6, 1)
            )
            self.spots_grid.add_widget(lbl)


# ─── PLACEHOLDER SCREENS ───────────────────────────────────
class WeatherScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_weather_cache()

        layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Top bar
        top_bar = BoxLayout(size_hint=(1, 0.08), spacing=10)
        back_btn = Button(text='⬅ Back', size_hint=(0.3, 1),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        top_bar.add_widget(back_btn)
        top_bar.add_widget(Label(text='🌤️ Weather', font_size='20sp', bold=True))
        layout.add_widget(top_bar)

        # GPS status
        self.gps_status = Label(
            text=self.get_gps_text(),
            font_size='15sp',
            size_hint=(1, 0.08),
            color=(0.4, 0.9, 0.4, 1)
        )
        layout.add_widget(self.gps_status)

        # Big fetch button
        fetch_btn = Button(
            text='📡 Get Weather at My Location',
            font_size='20sp',
            size_hint=(1, 0.13),
            background_color=(0.1, 0.5, 0.9, 1)
        )
        fetch_btn.bind(on_press=self.load_weather)
        layout.add_widget(fetch_btn)

        # Weather display
        self.weather_label = Label(
            text='Tap the button above\nto get weather at your location!',
            font_size='17sp',
            halign='center',
            valign='middle',
            size_hint=(1, 0.60)
        )
        self.weather_label.bind(size=self.weather_label.setter('text_size'))
        layout.add_widget(self.weather_label)

        # Status bar
        self.status_label = Label(
            text='',
            font_size='13sp',
            size_hint=(1, 0.07),
            color=(0.5, 0.9, 0.5, 1)
        )
        layout.add_widget(self.status_label)

        self.add_widget(layout)

    def get_gps_text(self):
        if gps_manager.lat:
            return f'📍 GPS: {gps_manager.lat:.4f}°, {gps_manager.lon:.4f}°'
        return '📡 GPS: Searching...'

    def on_enter(self):
        # Refresh GPS status every time screen opens
        self.gps_status.text = self.get_gps_text()

    def load_weather(self, btn):
        # Refresh GPS label
        self.gps_status.text = self.get_gps_text()

        if not gps_manager.lat:
            self.weather_label.text = (
                '⚠️ GPS not found yet!\n\n'
                'Please go to Map screen first\n'
                'and wait for GPS signal.'
            )
            return

        self.weather_label.text = '⏳ Fetching weather...'
        data, is_live, fetched_at = fetch_weather_by_coords(
            gps_manager.lat, gps_manager.lon
        )

        if data:
            advice = wind_advice(data['wind_speed'])
            source = '🟢 Live data' if is_live else '🔴 Offline cache'
            self.weather_label.text = (
                f'📍 {data["city"]}, {data["country"]}\n\n'
                f'🌡️  Temp:        {data["temperature"]}°C  '
                f'(Feels {data["feels_like"]}°C)\n'
                f'🌤️  Condition:  {data["description"]}\n'
                f'💧 Humidity:   {data["humidity"]}%\n'
                f'💨 Wind:        {data["wind_speed"]} km/h '
                f'{data["wind_dir"]}\n'
                f'🌧️  Rain:        {data["rain_1h"]} mm/hr\n'
                f'🌅 Sunrise:    {data["sunrise"]}\n'
                f'🌇 Sunset:     {data["sunset"]}\n\n'
                f'{advice}'
            )
            self.status_label.text = f'{source}  |  {fetched_at}'
        else:
            self.weather_label.text = (
                '❌ No weather data available.\n\n'
                'Connect to internet once\n'
                'to cache weather for offline use.'
            )
            self.status_label.text = ''


class DownloadScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text='⬇️ Download Maps\n\nComing in Phase 5!',
                                font_size='22sp', halign='center'))
        back_btn = Button(text='⬅ Back', size_hint=(1, 0.15),
                          background_color=(0.2, 0.2, 0.2, 1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        layout.add_widget(back_btn)
        self.add_widget(layout)


# ─── APP ENTRY POINT ───────────────────────────────────────
class FishNavApp(App):
    def build(self):
        init_db()
        return self.build_screens()

    def build_screens(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MapScreen(name='map'))
        sm.add_widget(SpotsScreen(name='spots'))
        sm.add_widget(WeatherScreen(name='weather'))
        sm.add_widget(DownloadScreen(name='download'))
        return sm


if __name__ == '__main__':
    FishNavApp().run()