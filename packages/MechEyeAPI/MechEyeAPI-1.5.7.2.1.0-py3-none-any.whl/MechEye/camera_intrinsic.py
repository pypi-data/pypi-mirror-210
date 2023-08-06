import _MechEye

class CameraIntrinsic:
    def __init__(self, impl):
        if not isinstance(impl, _MechEye.CameraIntrinsic):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(impl), type(_MechEye.CameraIntrinsic)
                )
            )
        self.__impl = impl

    def __str__(self):
        return str(self.__impl)

    def impl(self):
        return self.__impl

    def dist_coeffs_k1(self):
        return self.__impl.dist_coeffs_k1()

    def dist_coeffs_k2(self):
        return self.__impl.dist_coeffs_k2()

    def dist_coeffs_p1(self):
        return self.__impl.dist_coeffs_p1()

    def dist_coeffs_p2(self):
        return self.__impl.dist_coeffs_p2()

    def dist_coeffs_k3(self):
        return self.__impl.dist_coeffs_k3()

    
    def camera_matrix_fx(self):
        return self.__impl.camera_matrix_fx()

    def camera_matrix_fy(self):
        return self.__impl.camera_matrix_fy()
    
    def camera_matrix_cx(self):
        return self.__impl.camera_matrix_cx()
    
    def camera_matrix_cy(self):
        return self.__impl.camera_matrix_cy()