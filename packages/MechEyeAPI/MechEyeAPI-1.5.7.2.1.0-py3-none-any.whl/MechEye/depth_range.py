import _MechEye

class DepthRange:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.DepthRange):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.DepthRange)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def lower(self):
        impl = self.__impl
        return str(impl.lower())

    def upper(self):
        impl = self.__impl
        return str(impl.upper())

