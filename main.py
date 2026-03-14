from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class HomeScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15

        # App Title
        self.add_widget(Label(
            text='🐟 FishNav',
            font_size='32sp',
            bold=True,
            size_hint=(1, 0.2)
        ))

        # Big simple buttons for fishermen
        buttons = [
            ('🗺️  Map',           'green'),
            ('📍  My Spots',      'blue'),
            ('🌤️  Weather',       'orange'),
            ('⬇️  Download Maps', 'purple'),
        ]

        for label, color in buttons:
            btn = Button(
                text=label,
                font_size='22sp',
                size_hint=(1, 0.2),
                background_color=self.get_color(color)
            )
            self.add_widget(btn)

    def get_color(self, name):
        colors = {
            'green':  (0.1, 0.7, 0.3, 1),
            'blue':   (0.1, 0.4, 0.8, 1),
            'orange': (0.9, 0.5, 0.1, 1),
            'purple': (0.5, 0.1, 0.8, 1),
        }
        return colors.get(name, (0.5, 0.5, 0.5, 1))


class FishNavApp(App):
    def build(self):
        return HomeScreen()


if __name__ == '__main__':
    FishNavApp().run()