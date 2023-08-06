import _MechEye
import numpy

class PointXYZBGR:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.PointXYZBGR):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.PointXYZBGR)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def width(self):
        return self.__impl.width()

    def height(self):
        return self.__impl.height()  

    def data(self):
        """Copy image data to numpy array.

        Returns:
            A numpy array containing point_xyz_bgr pixel data
        """
        return numpy.array(self.__impl)

    def empty(self):
        return self.__impl.empty()  

    def release(self):
        self.__impl.release()    