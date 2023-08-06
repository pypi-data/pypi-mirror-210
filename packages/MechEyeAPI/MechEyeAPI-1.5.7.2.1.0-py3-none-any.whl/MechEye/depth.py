import _MechEye
import numpy

class Depth:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.Depth):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.Depth)
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

    def empty(self):
        return self.__impl.empty()  

    def release(self):
        self.__impl.release()

    def data(self):
        """Copy image data to numpy array.

        Returns:
            A numpy array containing depth pixel data
        """
        return numpy.array(self.__impl)

