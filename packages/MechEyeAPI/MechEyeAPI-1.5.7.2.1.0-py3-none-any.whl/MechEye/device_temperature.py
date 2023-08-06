import _MechEye

class DeviceTemperature:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.DeviceTemperature):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.DeviceTemperature)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def cpu_temperature(self):
        return self.__impl.cpu_temperature()

    def projector_module_temperature(self):
        return self.__impl.projector_module_temperature()
