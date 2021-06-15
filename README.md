# location地理位置计算

example
```
placeA = Location(104.061029, 30.543533)
placeB = Location(104.061029, 30.552567)

print(placeA.geohash)
print(placeA.calculate_distance_from_loc(placeB))
print(placeA.get_critical_point(1000))
```
输出
```
wm3vzbqbvx
1000.0538435427736
(104.071518, 104.05054, 30.552567, 30.534499)
```
