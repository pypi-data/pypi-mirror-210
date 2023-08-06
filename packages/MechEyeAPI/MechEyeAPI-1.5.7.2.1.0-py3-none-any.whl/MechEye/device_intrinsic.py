import _MechEye

class DeviceIntrinsic:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.DeviceIntrinsic):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.DeviceIntrinsic)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def texture_camera_intrinsic(self):
        return self.__impl.texture_camera_intrinsic()

    def depth_camera_intrinsic(self):
        return self.__impl.depth_camera_intrinsic()

    def depth_to_texture(self):
        return self.__impl.depth_to_texture()