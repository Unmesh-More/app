# map_screen.py
# FishNav Map Screen with live GPS dot and offline tile support

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy_garden.mapview import MapView, MapMarker
from database import save_spot_to_db, save_route_point


class MapScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tracking = False
        self.spot_count = 0
        self.gps_marker = None

        layout = BoxLayout(orientation='vertical')

        # ── Top bar ──────────────────────────────────────
        top_bar = BoxLayout(size_hint=(1, 0.07), spacing=8,
                            padding=[8, 4])
        back_btn = Button(text='⬅ Back', size_hint=(0.25, 1),
                          background_color=(0.15, 0.15, 0.15, 1))
        back_btn.bind(on_press=self.go_back)

        self.gps_label = Label(
            text='📡 Searching GPS...',
            font_size='14sp',
            color=(0.3, 1, 0.3, 1)
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(self.gps_label)
        layout.add_widget(top_bar)

        # ── Map view ─────────────────────────────────────
        # Default center: Arabian Sea near Mumbai coast
        self.mapview = MapView(
            zoom=8,
            lat=15.0,
            lon=73.0
        )
        layout.add_widget(self.mapview)

        # ── Bottom buttons ────────────────────────────────
        bottom_bar = BoxLayout(size_hint=(1, 0.10), spacing=8,
                               padding=[8, 4])
        self.save_btn = Button(
            text='📍 Save Spot',
            font_size='17sp',
            background_color=(0.1, 0.5, 0.9, 1)
        )
        self.track_btn = Button(
            text='🔴 Start Track',
            font_size='17sp',
            background_color=(0.8, 0.15, 0.15, 1)
        )
        self.save_btn.bind(on_press=self.save_spot)
        self.track_btn.bind(on_press=self.toggle_tracking)
        bottom_bar.add_widget(self.save_btn)
        bottom_bar.add_widget(self.track_btn)
        layout.add_widget(bottom_bar)

        self.add_widget(layout)

    def on_enter(self):
        from main import gps_manager
        gps_manager.on_location_callback = self.update_gps
        Clock.schedule_interval(self.refresh_gps, 2)

    def on_leave(self):
        Clock.unschedule(self.refresh_gps)

    def refresh_gps(self, dt):
        from main import gps_manager
        if gps_manager.lat:
            self.update_gps(gps_manager.lat, gps_manager.lon)

    def update_gps(self, lat, lon):
        # Update label
        self.gps_label.text = f'📍 {lat:.5f}°, {lon:.5f}°'

        # Move map to GPS position
        self.mapview.center_on(lat, lon)

        # Remove old marker and add new one
        if self.gps_marker:
            self.mapview.remove_marker(self.gps_marker)
        self.gps_marker = MapMarker(lat=lat, lon=lon)
        self.mapview.add_marker(self.gps_marker)

    def save_spot(self, btn):
        from main import gps_manager
        if gps_manager.lat:
            self.spot_count += 1
            name = f'Spot {self.spot_count}'
            save_spot_to_db(name, gps_manager.lat, gps_manager.lon)
            # Add a permanent marker on map
            marker = MapMarker(
                lat=gps_manager.lat,
                lon=gps_manager.lon,
                source='atlas://data/images/defaulttheme/checkbox_on'
            )
            self.mapview.add_marker(marker)
            self.gps_label.text = f'✅ {name} saved!'
        else:
            self.gps_label.text = '⚠️ No GPS signal yet!'

    def toggle_tracking(self, btn):
        self.tracking = not self.tracking
        if self.tracking:
            self.track_btn.text = '⏹️ Stop Track'
            self.track_btn.background_color = (0.3, 0.3, 0.3, 1)
            Clock.schedule_interval(self.record_route_point, 5)
        else:
            self.track_btn.text = '🔴 Start Track'
            self.track_btn.background_color = (0.8, 0.15, 0.15, 1)
            Clock.unschedule(self.record_route_point)
            self.gps_label.text = '⏹️ Route saved!'

    def record_route_point(self, dt):
        from main import gps_manager
        if gps_manager.lat:
            save_route_point(gps_manager.lat, gps_manager.lon)

    def go_back(self, btn):
        self.manager.current = 'home'