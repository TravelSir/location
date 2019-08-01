import math

EA = 6378137  # 赤道半径
EB = 6356725  # 极半径
WRONG_LAT = 'lat must be range -90 to 90'
WRONG_LNG = 'lng must be range -180 to 180'


def check_lat(lat=None, lat_list=[]):
    if lat and (lat < -90 or lat > 90):
        return False
    for l in lat_list:
        if l < -90 or l > 90:
            return False
    return True


def check_lng(lng=None, lng_list=[]):
    if lng and (lng < -180 or lng > 180):
        return False
    for l in lng_list:
        if l < -180 or l > 180:
            return False
    return True


def _get_correct_radii(lat):
    """
    由于地球是个椭圆，所计算的半径随着纬度变化也会产生变化
    :param lat: 纬度
    :return: 修正过后的半径
    """
    if not check_lat(lat):
        return WRONG_LAT
    return EB + (EB - EA) * (90.0 - lat) / 90.0


def _get_radian(degrees):
    """
    弧度的定义：弧长等于半径的弧,其所对的圆心角为1弧度
    360°=2π弧度
    经纬度的度数/360=弧度/2π
    :param degrees: 度数
    :return: 弧度
    """
    return math.pi * degrees / 180


def _get_degrees(radian):
    """
    弧度转换为角度，因为经纬度是角度
    :param radian: 弧度
    :return: 角度
    """
    return 180 * radian / math.pi


def _haversin(theta):
    """
    haversine公式: haversin(α) = sin²(α/2)
    """
    v = math.sin(theta / 2)
    return v * v


def get_distance_by_two_locations(lng1, lat1, lng2, lat2):
    """
    利用haversine公式求距离
    haversin(d/R) = haversin(φ2-φ1) + cos(φ1) * cos(φ2) * haversin(Δλ)
    其中
    haversin(α) = sin²(α/2) = (1-cos(α))/2
    R为地球半径；
    φ1, φ2 表示两点的纬度；
    Δλ 表示两点经度的差值。
    :param lng1: 第一个点的经度
    :param lat1: 第一个点的纬度
    :param lng2: 第二个点的经度
    :param lat2: 第二个点的纬度
    :return: distance 距离
    """
    if not check_lat(lat_list=[lat1, lat2]):
        return WRONG_LAT

    if not check_lng(lng_list=[lng1, lng2]):
        return WRONG_LNG

    radii = _get_correct_radii(lat1)

    # 公式计算用的是弧度，而经纬度是角度，需转换
    lng1 = _get_radian(lng1)
    lat1 = _get_radian(lat1)
    lng2 = _get_radian(lng2)
    lat2 = _get_radian(lat2)

    # 取差值,因为距离应该是正整数
    dlng = math.fabs(lng1 - lng2)
    dlat = math.fabs(lat1 - lat2)

    # 根据公式先开始计算右边
    tem = _haversin(dlat) + math.cos(lat1) * math.cos(lat2) * _haversin(dlng)

    # 再解左边公式求距离
    distance = 2 * radii * math.asin(math.sqrt(tem))

    return distance


def get_critical_point(distance, lng, lat):
    """
    利用haversine公式求经纬度的临界点

    :param distance: 距离
    :param lng: 经度
    :param lat: 纬度
    :return: max_lng,min_lng,max_lat,min_lat: 经纬度的临界值
    """
    if not check_lat(lat):
        return WRONG_LAT

    if not check_lng(lng):
        return WRONG_LNG

    # 首先计算公式左边
    radii = _get_correct_radii(lat)
    tem = _haversin(distance / radii)

    lat1 = _get_radian(lat)
    # 1.纬度相同
    lng_abs = math.asin(math.sqrt(tem / math.cos(lat1) / math.cos(lat1))) * 2
    lng_abs = _get_degrees(lng_abs)
    max_lng = lng + lng_abs
    min_lng = lng - lng_abs

    # 2.经度相同,Δλ=0，则cos(φ1) * cos(φ2) * haversin(Δλ) = 0,则haversin(d/R) = haversin(φ2-φ1)
    lat_abs = distance / radii
    lat_abs = _get_degrees(lat_abs)
    max_lat = lat + lat_abs
    min_lat = lat - lat_abs
    return max_lng, min_lng, max_lat, min_lat
