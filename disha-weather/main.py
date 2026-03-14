from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from weather_api import get_weather
from internet_check import is_connected


class WeatherPage(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        self.title = Label(
            text="DISHA WEATHER",
            font_size=30,
            size_hint=(1,0.2)
        )

        self.weather_info = Label(
            text="Press Refresh to Load Weather",
            font_size=18
        )

        self.refresh_button = Button(
            text="Refresh Weather",
            size_hint=(1,0.2)
        )

        self.refresh_button.bind(on_press=self.load_weather)

        self.add_widget(self.title)
        self.add_widget(self.weather_info)
        self.add_widget(self.refresh_button)


    def load_weather(self, instance):

        if not is_connected():

            self.weather_info.text = (
                "Weather Unavailable\n\n"
                "No Internet Connection"
            )

            return

        # Example coordinates (Mumbai)
        lat = 19.076019
        lon = 72.778221

        data = get_weather(lat, lon)

        if data:

            self.weather_info.text = f"""
Location: {data['city']}

Temperature: {data['temperature']}°C
Wind Speed: {data['wind_speed']} m/s
Humidity: {data['humidity']}%

Condition: {data['description']}
"""

        else:

            self.weather_info.text = "Weather Data Could Not Be Loaded"


class DishaWeatherApp(App):

    def build(self):
        return WeatherPage()


if __name__ == "__main__":
    DishaWeatherApp().run()