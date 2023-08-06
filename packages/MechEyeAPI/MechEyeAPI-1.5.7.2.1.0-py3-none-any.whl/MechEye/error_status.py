import _MechEye

class ErrorStatus:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.ErrorStatus):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.ErrorStatus)
                )
            )
        self.__impl = impl

    def ok(self):
        return bool(self.__impl.ok())

    def code(self):
        return int(self.__impl.code())

    def description(self):
        return str(self.__impl.description())

    @staticmethod
    def modeerror():
        raise ValueError("Please enter the correct mode")