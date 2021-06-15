import math

from geohash import encode_location

EA = 6378137  # 赤道半径
EB = 6356725  # 极半径


class Location:
    def __init__(self, lng, lat):
        self.lng = self.check_lng(lng)
        self.lat = self.check_lat(lat)
        self.radian_lng = self._get_radian(self.lng)
        self.radian_lat = self._get_radian(self.lat)
        self.radii = self._get_correct_radii()

    @property
    def geohash(self) -> str:
        return encode_location(self.lat, self.lng)

    @staticmethod
    def check_lat(lat: float) -> float:
        if lat and (lat < -90 or lat > 90):
            raise ValueError('lat must be range -90 to 90')
        return lat

    @staticmethod
    def check_lng(lng: float) -> float:
        if lng and (lng < -180 or lng > 180):
            raise ValueError('lng must be range -180 to 180')
        return lng

    @staticmethod
    def _get_radian(degrees: float) -> float:
        """
        弧度的定义：弧长等于半径的弧,其所对的圆心角为1弧度
        360°=2π弧度
        经纬度的度数/360=弧度/2π
        :param degrees: 度数
        :return: 弧度
        """
        return math.pi * degrees / 180

    def _get_correct_radii(self) -> float:
        """
        由于地球是个椭圆，所计算的半径随着纬度变化也会产生变化
        :param lat: 纬度
        :return: 修正过后的半径
        """

        return EB + (EB - EA) * (90.0 - self.lat) / 90.0

    @staticmethod
    def _get_degrees(radian):
        """
        弧度转换为角度，因为经纬度是角度
        :param radian: 弧度
        :return: 角度
        """
        return 180 * radian / math.pi

    @staticmethod
    def _haversin(theta):
        """
        haversine公式: haversin(α) = sin²(α/2)
        """
        v = math.sin(theta / 2)
        return v * v

    def calculate_distance_from_loc(self, target_place) -> float:
        """
        利用haversine公式求距离
        haversin(d/R) = haversin(φ2-φ1) + cos(φ1) * cos(φ2) * haversin(Δλ)
        其中
        haversin(α) = sin²(α/2) = (1-cos(α))/2
        R为地球半径；
        φ1, φ2 表示两点的纬度；
        Δλ 表示两点经度的差值。
        :param target_place: 目标点
        :return: distance 距离
        """

        if not isinstance(target_place, Location):
            raise TypeError('you must init a Location type as target_place')

        # 取差值,因为距离应该是正整数
        dlng = math.fabs(self.radian_lng - target_place.radian_lng)
        dlat = math.fabs(self.radian_lat - target_place.radian_lat)

        # 根据公式先开始计算右边
        tem = self._haversin(dlat) + math.cos(self.radian_lat) * math.cos(target_place.radian_lat) * self._haversin(dlng)

        # 再解左边公式求距离
        distance = 2 * self.radii * math.asin(math.sqrt(tem))

        return distance

    def get_critical_point(self, distance) -> (float, float, float, float):
        """
        利用haversine公式求经纬度的临界点

        :param distance: 距离
        :return: max_lng,min_lng,max_lat,min_lat: 经纬度的临界值
        """

        # 首先计算公式左边
        tem = self._haversin(distance / self.radii)

        # 1.纬度相同
        lng_abs = math.asin(math.sqrt(tem / math.cos(self.radian_lat) / math.cos(self.radian_lat))) * 2
        lng_abs = self._get_degrees(lng_abs)
        max_lng = self.lng + lng_abs
        min_lng = self.lng - lng_abs

        # 2.经度相同,Δλ=0，则cos(φ1) * cos(φ2) * haversin(Δλ) = 0,则haversin(d/R) = haversin(φ2-φ1)
        lat_abs = distance / self.radii
        lat_abs = self._get_degrees(lat_abs)
        max_lat = self.lat + lat_abs
        min_lat = self.lat - lat_abs
        return round(max_lng, 6), round(min_lng, 6), round(max_lat, 6), round(min_lat, 6)


if __name__ == '__main__':
    placeA = Location(104.061029, 30.543533)
    placeB = Location(104.061029, 30.552567)

    print(placeA.geohash)
    print(placeA.calculate_distance_from_loc(placeB))
    print(placeA.get_critical_point(1000))


