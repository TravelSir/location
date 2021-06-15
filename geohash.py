
LOC_BITS = 25  # 经纬度二进制长度都为25时，geohash长度为10，误差范围在0.5m内

B32_DIGIT = "0123456789bcdefghjkmnpqrstuvwxyz"


def encode_location(lat: float, lng: float) -> str:
    """
    将经纬度转化为geohash表示，并按奇数位纬度，偶数位经度组合，从0开始0算偶数
    :param lat: 纬度, 范围在-90～90
    :param lng: 经度, 范围在-180~180
    :return:
    """
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        raise TypeError("lat and lng must be int or float")

    if lat < -90 or lat > 90:
        raise ValueError("lat must be between -90 and 90")

    if lng < -180 or lng > 180:
        raise ValueError("lng must be between -180 and 180")

    lat_bits = get_binary(lat, -90, 90)
    lng_bits = get_binary(lng, -180, 180)

    # 合并两个二进制
    res_bits = [lat_bits[i // 2] if i % 2 else lng_bits[i // 2] for i in range(LOC_BITS * 2)]

    # 转十进制Base32编码
    res_int = [int(''.join(res_bits[i:i+5]), 2) for i in range(0, len(res_bits), 5)]
    geohash_str = "".join([B32_DIGIT[i] for i in res_int])

    return geohash_str


def get_binary(loc: float, left: float, right: float) -> str:
    """
    将经度或纬度转化为二进制集合
    左右区间划分为左闭右开
    :param loc: 经纬度
    :param left: 区间左边界
    :param right: 区间右边界
    :return:
    """
    _bin = ""
    for i in range(LOC_BITS):
        mid = (right + left) / 2
        if loc >= mid:
            _bin += "1"
            left = mid
        else:
            _bin += "0"
            right = mid
    return _bin



