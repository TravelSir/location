from typing import List

LOC_BITS = 25  # 经纬度二进制长度都为25时，geohash长度为10，误差范围在0.5m内

B32_DIGIT = "0123456789bcdefghjkmnpqrstuvwxyz"

# 精度表
PRECISION = {
    1: (3, 2),
    2: (5, 5),
    3: (8, 7),
    4: (10, 10),
    5: (13, 12),
    6: (15, 15),
    7: (18, 17),
    8: (20, 20),
    9: (22, 23),
    10: (25, 25),
    11: (28, 27),
    12: (30, 30)
}


def encode_location(lng: float, lat: float) -> str:
    """
    将经纬度转化为geohash表示，并按奇数位纬度，偶数位经度组合，从0开始0算偶数
    :param lng: 经度, 范围在-180~180
    :param lat: 纬度, 范围在-90～90
    :return:
    """
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        raise TypeError("lat and lng must be int or float")

    if lng < -180 or lng > 180:
        raise ValueError("lng must be between -180 and 180")

    if lat < -90 or lat > 90:
        raise ValueError("lat must be between -90 and 90")

    lng_bits = get_binary(lng, -180, 180)
    lat_bits = get_binary(lat, -90, 90)

    # 合并两个二进制
    res_bits = [lat_bits[i // 2] if i % 2 else lng_bits[i // 2] for i in range(LOC_BITS * 2)]

    # 转十进制Base32编码
    res_int = [int(''.join(res_bits[i:i+5]), 2) for i in range(0, len(res_bits), 5)]
    geohash_str = "".join([B32_DIGIT[i] for i in res_int])

    return geohash_str


def decode_geohash(hash_str: str) -> (float, float):
    """
    将geohash字符串解码出具体经纬度坐标(范围中间点)
    :param hash_str: geohash字符串
    :return:
    """
    res_bits = []
    for s in hash_str:
        _binary = bin(B32_DIGIT.find(s))
        _binary = '%5s' % _binary[2:]  # 指定宽度5
        for i in _binary:
            res_bits.append('0' if i == ' ' else i)  # 组合出总二进制串

    lng_bits = [r for i, r in enumerate(res_bits) if not i % 2]  # 经度二进制
    lat_bits = [r for i, r in enumerate(res_bits) if i % 2]  # 纬度二进制

    lng = get_degree(lng_bits, -180, 180)
    lat = get_degree(lat_bits, -90, 90)

    return round(lng, 6), round(lat, 6)


def get_around_hash_list(hash_str: str) -> List[str]:
    """
    计算周围8区域的geohash值，返回顺序为从左往右从上到下
    :param hash_str: 所在区域geohash值
    :return:
    """
    hash_len = len(hash_str)
    if hash_len < 1 or hash_len > 12:
        raise ValueError('geohash length must be less than 13')

    lng, lat = decode_geohash(hash_str)  # 当前坐标点

    lng_length, lat_length = PRECISION[len(hash_str)]

    min_lng = get_min_degree(360, lng_length)
    min_lat = get_min_degree(180, lat_length)

    hash_list = list()
    # 左上
    hash_list.append(encode_location(lng - min_lng, lat + min_lat))
    # 上
    hash_list.append(encode_location(lng, lat + min_lat))
    # 右上
    hash_list.append(encode_location(lng + min_lng, lat + min_lat))
    # 左
    hash_list.append(encode_location(lng - min_lng, lat))
    # 右
    hash_list.append(encode_location(lng + min_lng, lat))
    # 左下
    hash_list.append(encode_location(lng - min_lng, lat - min_lat))
    # 下
    hash_list.append(encode_location(lng, lat - min_lat))
    # 右下
    hash_list.append(encode_location(lng + min_lng, lat - min_lat))

    return hash_list


def get_binary(degree: float, left: float, right: float) -> str:
    """
    将经度或纬度转化为二进制集合
    左右区间划分为左闭右开
    :param degree: 角度(经纬度)
    :param left: 区间左边界
    :param right: 区间右边界
    :return:
    """
    _bin = ""
    for i in range(LOC_BITS):
        mid = (right + left) / 2
        if degree >= mid:
            _bin += "1"
            left = mid
        else:
            _bin += "0"
            right = mid
    return _bin


def get_degree(binary: List[str], left: float, right: float) -> float:
    """
    根据二进制得到具体经纬度(取结果范围中间点)
    :param binary: 二进制数组
    :param left: 区间左边界
    :param right: 区间右边界
    :return:
    """
    for b in binary:
        mid = (right + left) / 2
        if b == '1':
            left = mid
        else:
            right = mid
    return (right + left) / 2


def get_min_degree(scope: float, times: int) -> float:
    """
    根据经纬度拆分次数获取最小单位角度
    :param scope: 拆分区间总大小
    :param times: 拆分次数
    :return:
    """
    while times:
        times -= 1
        scope /= 2

    return scope


if __name__ == '__main__':
    print(decode_geohash('wm3vzbqbvx'))
    print(get_around_hash_list('wm3vzbqbvx'))

