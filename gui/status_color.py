def red():
    texture_data = []
    for i in range(0, 10 * 10):
        texture_data.append(255)
        texture_data.append(0)
        texture_data.append(0)
        texture_data.append(255)
    return texture_data

def green():
    texture_data = []
    for i in range(0, 10 * 10):
        texture_data.append(0)
        texture_data.append(255)
        texture_data.append(0)
        texture_data.append(255)
    return texture_data