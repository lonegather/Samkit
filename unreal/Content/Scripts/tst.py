from pprint import pprint


class FVector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return 'FVector <%s, %s, %s>' % (self.x, self.y, self.z)


class FRotator:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return 'FRotator <%s, %s, %s>' % (self.x, self.y, self.z)


curves = [
    {
        'object': 'MainCam',
        'class': 'FbxNode',
        'property': 'Lcl Translation',
        'channels': [
            {
                'name': 'X',
                'keys': [
                    (0.0, -200.0),
                    (1.0, -168.75),
                    (2.0, -100.0),
                    (3.0, -31.25),
                    (4.0, 0.0)
                ]
            },
            {
                'name': 'Y',
                'keys': [
                    (0.0, 50.0)
                ]
            },
            {
                'name': 'Z',
                'keys': [
                    (0.0, 0.0),
                    (1.0, 31.25),
                    (2.0, 100.0),
                    (3.0, 168.75),
                    (4.0, 200.0)
                ]
            }
        ]
    },
    {
        'object': 'MainCam',
        'class': 'FbxNode',
        'property': 'Lcl Rotation',
        'channels': [
            {
                'name': 'X',
                'keys': [
                    (0.0, -200.0),
                    (1.0, -168.75),
                    (2.0, -100.0),
                    (3.0, -31.25),
                    (4.0, 0.0)
                ]
            },
            {
                'name': 'Y',
                'keys': [
                    (0.0, 50.0)
                ]
            },
            {
                'name': 'Z',
                'keys': [
                    (0.0, 0.0),
                    (1.0, 31.25),
                    (2.0, 100.0),
                    (3.0, 168.75),
                    (4.0, 200.0)
                ]
            }
        ]
    }
]

channel_map = {
    'Lcl Translation': {'X': 0, 'Y': 2, 'Z': 1},
    'Lcl Rotation': {'X': 0, 'Y': 1, 'Z': 2},
}
trans_map = {
    'Lcl Translation': FVector,
    'Lcl Rotation': FRotator,
}
keys = {}
for curve in curves:
    prop = curve['property']
    if trans_map.get(prop, None):
        tmp = {}
        for channel in curve['channels']:
            index = channel_map[prop][channel['name']]
            frame, value = zip(*channel['keys'])
            for i in range(len(frame)):
                if not tmp.get(frame[i], None):
                    tmp[frame[i]] = [None, None, None]
                for k in tmp:
                    if k >= frame[i]:
                        tmp[k][index] = value[i]
        for k, v in tmp.items():
            if not keys.get(k, None):
                keys[k] = []
            keys[k].append(trans_map[prop](*v))

pprint(keys)
