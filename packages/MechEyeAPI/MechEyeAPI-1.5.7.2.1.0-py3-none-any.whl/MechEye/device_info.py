import _MechEye

class DeviceInfo:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.DeviceInfo):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.DeviceInfo)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    @property
    def model(self):
        return str(self.__impl.model())

    @property
    def id(self):
        return str(self.__impl.id())

    @property
    def hardware_version(self):
        return str(self.__impl.hardware_version())

    @property
    def firmware_version(self):
        return str(self.__impl.firmware_version())

    @property
    def ip(self):
        return str(self.__impl.ip())

    @property
    def port(self):
        return str(self.__impl.port())