import _MechEye

class LaserSettings:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.LaserSettings):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.LaserSettings)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def fringe_coding_mode(self):
        return self.__impl.fringe_coding_mode()

    def frame_range_start(self):
        return self.__impl.frame_range_start()  

    def frame_range_end(self):
        return self.__impl.frame_range_end()  

    def frame_partition_count(self):
        return self.__impl.frame_partition_count() 
        
    def power_level(self):
        return self.__impl.power_level()