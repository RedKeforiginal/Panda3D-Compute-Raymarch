from panda3d.core import loadPrcFileData

# Configure window size before loading ShowBase
loadPrcFileData('', 'win-size 1024 1024')

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame


class MainMenuApp(ShowBase):
    """Application with a simple main menu."""

    def __init__(self):
        super().__init__()
        self._build_menu()

    def _build_menu(self):
        frame = DirectFrame(
            frameColor=(0, 0, 0, 1),
            frameSize=(-0.6, 0.6, -0.8, 0.8),
            pos=(0, 0, 0),
        )

        button_scale = 0.1
        spacing = 0.2

        DirectButton(
            text="Launch",
            scale=button_scale,
            pos=(0, 0, spacing),
            command=self._on_launch,
            parent=frame,
        )
        DirectButton(
            text="Settings",
            scale=button_scale,
            pos=(0, 0, 0),
            command=self._on_settings,
            parent=frame,
        )
        DirectButton(
            text="Quit",
            scale=button_scale,
            pos=(0, 0, -spacing),
            command=self.userExit,
            parent=frame,
        )

    def _on_launch(self):
        print("Launch selected (placeholder)")

    def _on_settings(self):
        print("Settings selected (placeholder)")


if __name__ == "__main__":
    app = MainMenuApp()
    app.run()
