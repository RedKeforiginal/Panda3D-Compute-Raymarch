from panda3d.core import loadPrcFileData

# Configure window size before loading ShowBase
loadPrcFileData('', 'win-size 1024 1024')

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectButton, DirectFrame

from panda3d.core import Vec3, WindowProperties

class FirstPersonController:
    """Simple FPS camera controller using Panda3D input."""

    def __init__(self, base):
        self.base = base
        base.disableMouse()  # see Panda3D manual on disabling default mouse controls
        self.key_map = {"w": False, "a": False, "s": False, "d": False}
        for key in self.key_map:
            base.accept(key, self._set_key, [key, True])
            base.accept(f"{key}-up", self._set_key, [key, False])
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)
        self.center_x = base.win.getXSize() // 2
        self.center_y = base.win.getYSize() // 2
        base.win.movePointer(0, self.center_x, self.center_y)
        self.heading = 0.0
        self.pitch = 0.0
        self.speed = 5.0
        self.sensitivity = 0.2
        base.taskMgr.add(self.update, "fps-update")

    def _set_key(self, key, value):
        self.key_map[key] = value

    def update(self, task):
        dt = globalClock.getDt()
        if self.base.mouseWatcherNode.hasMouse():
            md = self.base.win.getPointer(0)
            dx = md.getX() - self.center_x
            dy = md.getY() - self.center_y
            self.heading -= dx * self.sensitivity
            self.pitch = max(-90, min(90, self.pitch - dy * self.sensitivity))
            self.base.camera.setHpr(self.heading, self.pitch, 0)
            self.base.win.movePointer(0, self.center_x, self.center_y)

        move = Vec3(0, 0, 0)
        if self.key_map["w"]:
            move.y += 1
        if self.key_map["s"]:
            move.y -= 1
        if self.key_map["a"]:
            move.x -= 1
        if self.key_map["d"]:
            move.x += 1
        if move.lengthSquared() > 0:
            move.normalize()
            self.base.camera.setPos(self.base.camera, move * self.speed * dt)
        return task.cont

class MainMenuApp(ShowBase):
    """Application with a simple main menu."""

    def __init__(self):
        super().__init__()
        self._build_menu()

    def _build_menu(self):
        self.menu_frame = DirectFrame(
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
            parent=self.menu_frame,
        )
        DirectButton(
            text="Settings",
            scale=button_scale,
            pos=(0, 0, 0),
            command=self._on_settings,
            parent=self.menu_frame,
        )
        DirectButton(
            text="Quit",
            scale=button_scale,
            pos=(0, 0, -spacing),
            command=self.userExit,
            parent=self.menu_frame,
        )

    def _on_launch(self):
        if hasattr(self, "menu_frame"):
            self.menu_frame.destroy()
        self.controller = FirstPersonController(self)

    def _on_settings(self):
        print("Settings selected (placeholder)")


if __name__ == "__main__":
    app = MainMenuApp()
    app.run()
