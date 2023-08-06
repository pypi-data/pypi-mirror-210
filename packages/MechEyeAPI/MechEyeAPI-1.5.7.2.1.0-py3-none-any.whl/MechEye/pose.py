import _MechEye

class Pose:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.Pose):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.Pose)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def rotation0(self):
        return self.__impl.rotation0()

    def rotation1(self):
        return self.__impl.rotation1()

    def rotation2(self):
        return self.__impl.rotation2()

    def rotation3(self):
        return self.__impl.rotation3()

    def rotation4(self):
        return self.__impl.rotation4()
    
    def rotation5(self):
        return self.__impl.rotation5()

    def rotation6(self):
        return self.__impl.rotation6()

    def rotation7(self):
        return self.__impl.rotation7()

    def rotation8(self):
        return self.__impl.rotation8()


    def translation0(self):
        return self.__impl.translation0()

    def translation1(self):
        return self.__impl.translation1()

    def translation2(self):
        return self.__impl.translation2()