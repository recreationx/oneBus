from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def findDistance(arr):
    def merge(left, right):
        sortedarray = []
        while len(left) > 0 and len(right) > 0:
            if left[0]["Distance"] > right[0]["Distance"]:
                elem = right.pop(0)
            else:
                elem = left.pop(0)
            sortedarray.append(elem)
        sortedarray = sortedarray + left + right
        return sortedarray

    def mergeSort(arr):
        if len(arr) > 1:
            mid = len(arr) // 2
            left = mergeSort(arr[:mid])
            right = mergeSort(arr[mid:])
            sortedarray = merge(left, right)
            return sortedarray
        else:
            return arr

    return mergeSort(arr)
