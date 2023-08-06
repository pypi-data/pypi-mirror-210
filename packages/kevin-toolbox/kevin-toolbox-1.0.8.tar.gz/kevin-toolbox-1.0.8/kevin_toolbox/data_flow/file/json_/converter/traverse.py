def traverse(x, converter):
    if converter is None:
        return x

    assert callable(converter)
    return recursive_(x, converter)


def recursive_(x, converter):
    if isinstance(x, list):
        for i, v in enumerate(x):
            x[i] = recursive_(v, converter)
    elif isinstance(x, dict):
        for k, v in x.items():
            x[k] = recursive_(v, converter)
    else:
        x = converter(x)
    return x


if __name__ == '__main__':
    import numpy as np

    print(traverse(x=[dict(d=3, c=4), np.array([[1, 2, 3]])],
                   converter=lambda x: x.tolist() if type(x) is np.ndarray else x))
    print(traverse(x=np.array([1, 2, 3]),
                   converter=lambda x: x.tolist() if type(x) is np.ndarray else x))
