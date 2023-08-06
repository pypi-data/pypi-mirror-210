import _MechEye
import numpy

class Color:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.Color):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.Color)
                )
            )
        self.__impl = impl

    def from_numpy(self, np):
        return  _MechEye.color_from_numpy_array(np)

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
            A numpy array containing color pixel data
        """
        return numpy.array(self.__impl)

    def empty(self):
        return self.__impl.empty()

    def release(self):
        self.__impl.release()            

   