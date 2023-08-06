import _MechEye
import warnings
from MechEye.device_info import DeviceInfo
from MechEye.device_temperature import DeviceTemperature
from MechEye.color import Color
from MechEye.error_status import ErrorStatus
from MechEye.resolution import Resolution
from MechEye.device_intrinsic import DeviceIntrinsic
from MechEye.depth import Depth
from MechEye.point_xyz import PointXYZ
from MechEye.point_xyz_bgr import PointXYZBGR
from MechEye.roi import Roi
from MechEye.depth_range import DepthRange
from MechEye.laser_settings import LaserSettings
from MechEye.uhp_settings import UhpSettings

class Device:
    def __init__(self):
        self.__impl = _MechEye.Device()

    def __str__(self):
        return str(self.__impl)

    @staticmethod
    def get_device_list():
        """ 
        Enumerates Mech-Eye devices 
        :return: Information on all detectable Mech-Eye devices.
        """
        return [DeviceInfo(internal_camera) for internal_camera in _MechEye.Device.enumerate_mecheye_device_list()]

    def connect(self, info):
        """
        Connects to the device.
        :param info: device information used to connect the device which can be obtained by get_device_list function.
        """
        if not isinstance(info, DeviceInfo):
            raise TypeError(
                "Unsupported type for argument impl. Got {}, expected {}".format(
                    type(info), type(DeviceInfo)
                )
            )

        impl = self.__impl
        return ErrorStatus(impl.connect(info.impl()))

    def connect_by_ip(self, ip, port = 5577, timeout = 10000):
        """
        Connects to the device.
        :param ip: ip address.
        :param port: device port number, defult 5577
        :param timeout: the timeout value (ms), default 10000
        """
        impl = self.__impl
        return ErrorStatus(impl.connect_by_ip(ip, port, timeout))

    def release(self):
        """
        Release the underlying resources.
        """
        try:
            impl = self.__impl
        except AttributeError:
            pass
        else:
            impl.release()

    def disconnect(self):
        """
        Disconnects from the device.
        """
        impl = self.__impl
        impl.disconnect()

    def get_device_info(self):
        """
        Gets the basic information about the connected device.
        :return: The info of connected device
        """
        impl = self.__impl
        return DeviceInfo(impl.get_device_info())

    def get_device_temperature(self):
        """
        Gets the temperature about the connected device.
        :return: The temperature value of connected device
        """
        impl = self.__impl
        return DeviceTemperature(impl.get_device_temperature())

    def get_device_intrinsic(self):
        """
        Gets the intrinsic camera parameter about the connected device.
        :return: Intrinsic See intrinsic.py for details
        """
        impl = self.__impl
        return DeviceIntrinsic(impl.get_device_intrinsic())

    def get_device_resolution(self):
        """
        Gets the device resolution.
        :return: Resolution See resolution.py for details
        """
        impl = self.__impl
        return Resolution(impl.get_device_resolution())

    def capture_color(self):
        """
        Captures a color image.
        :return: Color See color.py for details.
        """
        impl = self.__impl
        return Color(impl.capture_color())

    def capture_depth(self):
        """
        Captures a depth image.
        :return: Depth See depth.py for details
        """
        impl = self.__impl
        return Depth(impl.capture_depth())

    def capture_point_xyz(self):
        """
        Captures a point cloud image.
        :return: PointXYZ See point_xyz.py for details
        """
        impl = self.__impl
        return PointXYZ(impl.capture_point_xyz())

    def capture_point_xyz_bgr(self):
        """
        Captures a colored point cloud image.
        :return: PointXYZBGR See point_xyz_bgr.py for details
        """
        impl = self.__impl
        return PointXYZBGR(impl.capture_point_xyz_bgr())

    def get_cloud_from_texture_mask(self, depth, textureMask, intri):
        """
        Gets the point cloud image within the mask specified by the texture map.
        :param depth: Depth See depth.py for details
        :param textureMask: A color map within the mask. See color.py for details.
        :param intri: Intrinsic See intrinsic.py for details
        :return: PointXYZ See point_xyz.py for details
        """
        impl = self.__impl
        return PointXYZ(impl.get_cloud_from_texture_mask(depth, textureMask, intri))

    def get_bgr_cloud_from_texture_mask(self, depth, textureMask, texture, intri):
        """
        Gets the colored point cloud image within the mask specified by the texture map.
        :param depth: Depth See depth.py for details
        :param textureMask: A color map within the mask. See color.py for details.
        :param texture: Color See color.py for details.
        :param intri: Intrinsic See intrinsic.py for details
        :return: PointXYZBGR See point_xyz_bgr.py for details
        """
        impl = self.__impl
        return PointXYZBGR(impl.get_bgr_cloud_from_texture_mask(depth, textureMask, texture, intri))

    def set_scan_2d_exposure_mode(self, info):
        """
        Sets the camera exposure mode to capture the 2D images.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Timed": 0, "Auto": 1, "HDR":2, "Flash": 3}
        if info in dec:
            return ErrorStatus(impl.set_scan_2d_exposure_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_scan_2d_exposure_mode(self):
        """
        Gets the camera exposure mode to capture the 2D images.
        :return: 2Dsettings exposure mode
        """
        impl = self.__impl
        return impl.get_scan_2d_exposure_mode()

    def set_scan_2d_exposure_time(self, info):
        """
        Sets the camera exposure time.
        :param info: The data type is double.
        :return: See error_status.py for details.
        """
        if isinstance(info, (float, int),):
            impl = self.__impl
            return ErrorStatus(impl.set_scan_2d_exposure_time(info))
        else:
            raise TypeError("Unsupported type, expected: (float, int,), got {value_type}".format(
                        value_type=type(info)))

    def get_scan_2d_exposure_time(self):
        """
        Gets the camera exposure time in 2DSettings.
        :return: 2Dsettings exposure time
        """
        impl = self.__impl
        return impl.get_scan_2d_exposure_time()

    def set_scan_2d_hdr_exposure_sequence(self, info):
        """
        Sets the camera HDR exposure sequence.
        :param info: The valueSequence data type is double.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_2d_hdr_exposure_sequence(info))

    def get_scan_2d_hdr_exposure_sequence(self):
        """
        Gets the camera HDR exposure sequence in 2DSettings.
        :return: 2D settings exposure sequence.
        """
        impl = self.__impl
        return impl.get_scan_2d_hdr_exposure_sequence()

    def set_scan_2d_expected_gray_value(self, info):
        """
        Sets the expected gray value.
        :param info: The data type is int.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_2d_expected_gray_value(info))

    def get_scan_2d_expected_gray_value(self):
        """
        Gets the expected gray value in 2DSettings.
        :return: 2D settings expected gray value.
        """
        impl = self.__impl
        return impl.get_scan_2d_expected_gray_value()

    def set_scan_2d_tone_mapping_enable(self, info):
        """
        Sets whether gray level transformation algorithm is used or not.
        :param info: The data type is bool.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_2d_tone_mapping_enable(info))

    def get_scan_2d_tone_mapping_enable(self):
        """
        Gets whether gray level transformation algorithm is used or not.
        :return: The result of whether gray level transformation algorithm is used or not.
        """
        impl = self.__impl
        return impl.get_scan_2d_tone_mapping_enable()

    def set_scan_2d_sharpen_factor(self, info):
        """
        Sets the image sharpen factor.
        :param info: The data type is double.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_2d_sharpen_factor(info))

    def get_scan_2d_sharpen_factor(self):
        """
        Gets the image sharpen factor.
        :return: The value of sharpen factor.
        """
        impl = self.__impl
        return impl.get_scan_2d_sharpen_factor()

    def set_scan_2d_roi(self, x, y, width, height):
        """
        Sets ROI to capture the 2D image.
        :param x: The data type is unsigned.
        :param y: The data type is unsigned.
        :param width: The data type is unsigned.
        :param height: The data type is unsigned.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_2d_roi(x, y, width, height))

    def get_scan_2d_roi(self):
        """
        Gets ROI to capture the 2D image.
        :return: Roi See roi.py for details
        """
        impl = self.__impl
        return Roi(impl.get_scan_2d_roi())

    def set_scan_3d_exposure(self, info):
        """
        Sets the exposure time of the camera to capture the 3D image.
        :param info: The valueSequence data type is double.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_3d_exposure(info))

    def get_scan_3d_exposure(self):
        """
        Gets the exposure time sequence of the camera to capture the 3D image.
        :return: The result of exposure time sequence. 
        """
        impl = self.__impl
        return impl.get_scan_3d_exposure()

    def set_scan_3d_gain(self, info):
        """
        Sets gain to capture the 3d image.
        :param info: The data type is double.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_3d_gain(info))

    def get_scan_3d_gain(self):
        """
        Gets gain to capture the 3d image.
        :return: The value of gain.
        """
        impl = self.__impl
        return impl.get_scan_3d_gain()

    def set_scan_3d_roi(self, x, y, width, height):
        """
        Sets ROI to capture the 3D image.
        MechEye UHP serials in capture mode 'Merge' does not support this parameter.
        :param x: The data type is unsigned.
        :param y: The data type is unsigned.
        :param width: The data type is unsigned.
        :param height: The data type is unsigned.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_scan_3d_roi(x, y, width, height))

    def get_scan_3d_roi(self):
        """
        Gets ROI to capture the 3D image.
        :return: The value of 3D roi
        """
        impl = self.__impl
        return impl.get_scan_3d_roi()

    def set_depth_range(self, lower, upper):
        """
        Sets depth range in 3D image.
        :param lower: The data type is int.
        :param upper: The data type is int.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_depth_range(lower, upper))

    def get_depth_range(self):
        """
        Gets depth range in 3D image.
        :return: The value of depth range.
        """
        impl = self.__impl
        return DepthRange(impl.get_depth_range())

    def set_fringe_contrast_threshold(self, info):
        """
        Sets the signal contrast threshold for effective pixels.
        :param info: The data type is int.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_fringe_contrast_threshold(info))

    def get_fringe_contrast_threshold(self):
        """
        Gets the signal contrast threshold for effective pixels.
        :return: The value of FringeContrastThreshold.
        """
        impl = self.__impl
        return impl.get_fringe_contrast_threshold()

    def set_fringe_min_threshold(self, info):
        """
        Sets the signal minimum threshold for effective pixels.
        :param info: The data type is int.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_fringe_min_threshold(info))

    def get_fringe_min_threshold(self):
        """
        Gets the signal minimum threshold for effective pixels.
        :return: The value of FringeMinThreshold.
        """
        impl = self.__impl
        return impl.get_fringe_min_threshold()

    def set_cloud_outlier_filter_mode(self, info):
        """
        Sets the point cloud outliers removal algorithm.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        warnings.warn("set_cloud_outlier_filter_mode is deprecated, please use set_cloud_outlier_removal_mode instead", DeprecationWarning)
        impl = self.__impl
        dec = {"Off" : 0, "Weak": 1, "Normal": 2}
        if info in dec:
            return ErrorStatus(impl.set_cloud_outlier_filter_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_cloud_outlier_filter_mode(self):
        """
        Gets the point cloud outliers removal algorithm.
        :return: The value of OutlierFilterMode.
        """
        warnings.warn("get_cloud_outlier_filter_mode is deprecated, please use get_cloud_outlier_removal_mode instead", DeprecationWarning)
        impl = self.__impl
        return impl.get_cloud_outlier_filter_mode()

    def set_cloud_smooth_mode(self, info):
        """
        Sets the point cloud smoothing algorithm.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        warnings.warn("set_cloud_smooth_mode is deprecated, please use set_cloud_surface_smoothing_mode instead", DeprecationWarning)
        impl = self.__impl
        dec = {"Off":0, "Normal": 1, "Weak": 2, "Strong": 3}
        if info in dec:
            return ErrorStatus(impl.set_cloud_smooth_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_cloud_smooth_mode(self):
        """
        Gets the point cloud smoothing algorithm.
        :return: The value of SmoothMode.
        """
        warnings.warn("get_cloud_smooth_mode is deprecated, please use get_cloud_surface_smoothing_mode instead", DeprecationWarning)
        impl = self.__impl
        return impl.get_cloud_smooth_mode()

    def set_cloud_surface_smoothing_mode(self, info):
        """
        Sets the point cloud surface smoothing mode.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Off" : 0, "Weak": 1, "Normal": 2, "Strong": 3}
        if info in dec:
            return ErrorStatus(impl.set_cloud_surface_smoothing_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_cloud_surface_smoothing_mode(self):
        """
        Gets the point cloud surface smoothing mode.
        :return: Cloud surface smoothing mode
        """
        impl = self.__impl
        return impl.get_cloud_surface_smoothing_mode()

    def set_cloud_noise_removal_mode(self, info):
        """
        Sets the point cloud noise removal mode.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Off":0, "Weak": 1, "Normal": 2, "Strong": 3}
        if info in dec:
            return ErrorStatus(impl.set_cloud_noise_removal_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_cloud_noise_removal_mode(self):
        """
        Gets the point cloud noise removal mode.
        :return: Cloud noise removal mode
        """
        impl = self.__impl
        return impl.get_cloud_noise_removal_mode()

    def set_cloud_outlier_removal_mode(self, info):
        """
        Sets the point cloud outlier removal mode.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Off":0, "Weak": 1, "Normal": 2, "Strong": 3}
        if info in dec:
            return ErrorStatus(impl.set_cloud_outlier_removal_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_cloud_outlier_removal_mode(self):
        """
        Gets the point cloud outlier removal mode.
        :return: Cloud outlier removal mode
        """
        impl = self.__impl
        return impl.get_cloud_outlier_removal_mode()

    def set_cloud_edge_preservation_mode(self, info):
        """
        Sets the point cloud edge preservation mode.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Sharp":0, "Normal": 1, "Smooth": 2}
        if info in dec:
            return ErrorStatus(impl.set_cloud_edge_preservation_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_cloud_edge_preservation_mode(self):
        """
        Gets the point cloud edge preservation mode.
        :return: Cloud edge preservation mode
        """
        impl = self.__impl
        return impl.get_cloud_edge_preservation_mode()

    def set_projector_fringe_coding_mode(self, info):
        """
        Sets projector's fringe coding mode. 
        Only support with Mech-Eye NANO and PRO series industrial 3D cameras.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Fast": 0, "Accurate": 1}
        if info in dec:
            return ErrorStatus(impl.set_projector_fringe_coding_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_projector_fringe_coding_mode(self):
        """
        Gets projector's fringe coding mode. 
        Only support with Mech-Eye NANO and PRO series industrial 3D cameras.
        :return: The value of fringeCodingMode.
        """
        impl = self.__impl
        return impl.get_projector_fringe_coding_mode()
        
    def set_projector_power_level(self, info):
        """
        Sets projector's powerl level. 
        Only support with Mech-Eye NANO and PRO series industrial 3D cameras.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"High": 0, "Normal": 1, "Low": 2}
        if info in dec:
            return ErrorStatus(impl.set_projector_power_level(dec[info]))
        return ErrorStatus.modeerror()

    def get_projector_power_level(self):
        """
        Gets projector's powerl level. 
        Only support with Mech-Eye NANO and PRO series industrial 3D cameras.
        :return: The value of powerLevel.
        """
        impl = self.__impl
        return impl.get_projector_power_level()

    def set_projector_anti_flicker_mode(self, info):
        """
        Sets projector's anti-flicker mode. 
        Only support with Mech-Eye NANO and PRO series industrial 3D camera.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Off": 0, "AC50Hz": 1, "AC60Hz": 2}
        if info in dec:
            return ErrorStatus(impl.set_projector_anti_flicker_mode(dec[info]))
        return ErrorStatus.modeerror()

    def get_projector_anti_flicker_mode(self):
        """
        Gets projector's anti-flicker mode. 
        Only support with Mech-Eye NANO and PRO series industrial 3D camera.
        :return: The value of antiFlickerMode.
        """
        impl = self.__impl
        return impl.get_projector_anti_flicker_mode()

    def set_laser_settings(self, mode, start, end, count, level):
        """
        Sets laser settings for laser device.
        :param mode: The data type is string.
        :param start: The data type is int.
        :param end: The data type is int.
        :param count: The data type is int.
        :param level: The data type is int.
        :return: See error_status.py for details.
        """
        dec = {"Fast": 0, "Accurate": 1}
        impl = self.__impl
        if mode in dec:
            return ErrorStatus(impl.set_laser_settings(dec[mode], start, end, count, level))
        return ErrorStatus.modeerror()

    def get_laser_settings(self):
        """
        Gets laser settings for laser device.
        :return:The value of LaserSettings.
        """
        impl = self.__impl
        return LaserSettings(impl.get_laser_settings())

    def set_uhp_settings(self, capture_mode, fringe_coding_mode):
        """
        Sets uhp settings for uhp device.
        :param capture_mode: The data type is string.
        :param fringe_coding_mode: The data type is string.
        :return: See error_status.py for details.
        """
        dec_uhp_capture_mode = {"Camera1": 0, "Camera2": 1, "Merge": 2}
        dec_uhp_fringe_coding_mode = {"Fast": 0, "Accurate": 1}
        impl = self.__impl
        if capture_mode in dec_uhp_capture_mode and fringe_coding_mode in dec_uhp_fringe_coding_mode:
            return ErrorStatus(impl.set_uhp_settings(dec_uhp_capture_mode[capture_mode], dec_uhp_fringe_coding_mode[fringe_coding_mode]))
        return ErrorStatus.modeerror()

    def get_uhp_settings(self):
        """
        Gets uhp settings for uhp device.
        :return:The value of UhpSettings.
        """
        impl = self.__impl
        return UhpSettings(impl.get_uhp_settings())

    def set_uhp_capture_mode(self, mode):
        """
        Sets the uhp camera capture mode.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Camera1" : 0, "Camera2": 1, "Merge": 2}
        if mode in dec:
            return ErrorStatus(impl.set_uhp_capture_mode(dec[mode]))
        return ErrorStatus.modeerror()

    def get_uhp_capture_mode(self):
        """
        Gets the uhp camera capture mode.
        :return: The value of UhpCaptureMode. 
        """
        impl = self.__impl
        return impl.get_uhp_capture_mode()

    def set_uhp_fringe_coding_mode(self, mode):
        """
        Sets the uhp camera fringe coding mode.
        :param mode: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        dec = {"Fast" : 0, "Accurate" : 1}
        if mode in dec:
            return ErrorStatus(impl.set_uhp_fringe_coding_mode(dec[mode]))
        return ErrorStatus.modeerror()

    def get_uhp_fringe_coding_mode(self):
        """
        Gets the uhp camera fringe coding mode.
        :return: The value of UhpFringeCodingMode. 
        """
        impl = self.__impl
        return impl.get_uhp_fringe_coding_mode()

    def save_all_settings_to_user_set(self):
        """
        Saves all parameters to the current user set.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.save_all_settings_to_user_set())

    def set_current_user_set(self, info):
        """
        Sets the current user set by user set name.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.set_current_user_set(info))

    def get_current_user_set(self):
        """
        Gets the name of the current user set.
        :return:The value of userSetName.
        """
        impl = self.__impl
        return impl.get_current_user_set()

    def get_all_user_sets(self):
        """
        Gets the names of all user sets.
        :return: The value of all user sets
        """
        return [str(user_set) for user_set in self.__impl.get_all_user_sets()]

    def delete_user_set(self, info):
        """
        Deletes the user set by the user set name.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.delete_user_set(info))

    def add_user_set(self, info):
        """
        Adds a new user set by the user set name and set all the current device settings to it.
        :param info: The data type is string.
        :return: See error_status.py for details.
        """
        impl = self.__impl
        return ErrorStatus(impl.add_user_set(info))
