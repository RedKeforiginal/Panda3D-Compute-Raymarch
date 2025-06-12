from panda3d.core import WindowProperties, Vec3
from direct.showbase.ShowBase import ShowBase


class FPSCamera:
    """Simple first-person camera controller."""

    def __init__(self, base, speed=5.0, sensitivity=0.2):
        self.base = base
        self.speed = speed
        self.sensitivity = sensitivity
        self.pitch = 0.0
        self.yaw = 0.0

        self.key_map = {
            "forward": False,
            "backward": False,
            "left": False,
            "right": False,
            "up": False,
            "down": False,
        }

        base.disableMouse()
        self._setup_window()
        self._setup_controls()

        self.center_x = base.win.getXSize() // 2
        self.center_y = base.win.getYSize() // 2
        base.win.movePointer(0, self.center_x, self.center_y)

        base.taskMgr.add(self.update, "update_camera")

    def _setup_window(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        self.base.win.requestProperties(props)

    def _setup_controls(self):
        self.base.accept("w", self._set_key, ["forward", True])
        self.base.accept("w-up", self._set_key, ["forward", False])
        self.base.accept("s", self._set_key, ["backward", True])
        self.base.accept("s-up", self._set_key, ["backward", False])
        self.base.accept("a", self._set_key, ["left", True])
        self.base.accept("a-up", self._set_key, ["left", False])
        self.base.accept("d", self._set_key, ["right", True])
        self.base.accept("d-up", self._set_key, ["right", False])
        self.base.accept("space", self._set_key, ["up", True])
        self.base.accept("space-up", self._set_key, ["up", False])
        self.base.accept("control", self._set_key, ["down", True])
        self.base.accept("control-up", self._set_key, ["down", False])
        self.base.accept("escape", self.base.userExit)

    def _set_key(self, key, value):
        self.key_map[key] = value

    def update(self, task):
        dt = globalClock.getDt()
        if self.base.mouseWatcherNode.hasMouse():
            md = self.base.win.getPointer(0)
            x = md.getX()
            y = md.getY()
            dx = x - self.center_x
            dy = y - self.center_y

            self.yaw -= dx * self.sensitivity
            self.pitch -= dy * self.sensitivity
            self.pitch = max(-90.0, min(90.0, self.pitch))

            self.base.camera.setHpr(self.yaw, self.pitch, 0)
            self.base.win.movePointer(0, self.center_x, self.center_y)

        move_vec = Vec3(0, 0, 0)
        if self.key_map["forward"]:
            move_vec.y += 1
        if self.key_map["backward"]:
            move_vec.y -= 1
        if self.key_map["left"]:
            move_vec.x -= 1
        if self.key_map["right"]:
            move_vec.x += 1
        if self.key_map["up"]:
            move_vec.z += 1
        if self.key_map["down"]:
            move_vec.z -= 1

        if move_vec.length_squared() > 0:
            move_vec.normalize()
            move_vec *= self.speed * dt
            move_vec = self.base.camera.getQuat().xform(move_vec)
            self.base.camera.setPos(self.base.camera.getPos() + move_vec)

        return task.cont


class App(ShowBase):
    def __init__(self):
        super().__init__()
        self.setBackgroundColor(0.1, 0.1, 0.1)
        self.camera_controller = FPSCamera(self)


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
