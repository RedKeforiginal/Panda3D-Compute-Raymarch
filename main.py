from direct.showbase.ShowBase import ShowBase


class RaymarchApp(ShowBase):
    """Placeholder application for future ray marching demo."""

    def __init__(self):
        super().__init__()
        self.setFrameRateMeter(True)
        self.win.set_title("Panda3D Raymarch Placeholder")


if __name__ == "__main__":
    app = RaymarchApp()
    app.run()
