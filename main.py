from panda3d.core import loadPrcFileData
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame

# Set default window resolution
loadPrcFileData("", "win-size 1024 1024")


class RaymarchApp(ShowBase):
    """Placeholder application for future ray marching demo."""

    def __init__(self):
        super().__init__()
        self.setFrameRateMeter(True)
        self.win.set_title("Panda3D Raymarch Placeholder")

        # Setup a simple main menu with placeholder buttons.
        self.menu = DirectFrame(frameColor=(0, 0, 0, 0))

        y = 0.2
        btn_scale = 0.07

        self.launch_btn = DirectButton(
            text="Launch",
            scale=btn_scale,
            command=self._placeholder,
            pos=(0, 0, y),
        )
        self.launch_btn.reparentTo(self.menu)

        self.options_btn = DirectButton(
            text="Options",
            scale=btn_scale,
            command=self._placeholder,
            pos=(0, 0, y - 0.15),
        )
        self.options_btn.reparentTo(self.menu)

        self.quit_btn = DirectButton(
            text="Quit",
            scale=btn_scale,
            command=self.userExit,
            pos=(0, 0, y - 0.3),
        )
        self.quit_btn.reparentTo(self.menu)

    def _placeholder(self):
        """Placeholder callback for unimplemented menu actions."""
        print("Menu item selected (placeholder)")


if __name__ == "__main__":
    app = RaymarchApp()
    app.run()
