import _MechEye

class UhpSettings:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.UhpSettings):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.UhpSettings)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def capture_mode(self):
        return self.__impl.capture_mode()

    def fringe_coding_mode(self):
        return self.__impl.fringe_coding_mode()