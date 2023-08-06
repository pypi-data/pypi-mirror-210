import _MechEye

class Resolution:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.Resolution):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.Resolution)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def color_width(self):
        return str(self.__impl.color_width())
    
    def color_height(self):
        return str(self.__impl.color_height())

    def depth_width(self):
        return str(self.__impl.depth_width())

    def depth_height(self):
        return str(self.__impl.depth_height())
    