import cv2

def compare_color(image, point, color, tolerance=0):
    """
    比较某一图像中某点的颜色值是否和传入颜色参数值相等。

    参数：
    - image: 图像 Mat格式
    - point: 坐标点 Point[x,y]
    - color: 需要比较的颜色值，例如 "#FF0000" 表示红色
    - tolerance: 允许的颜色差异程度

    返回值：
    - 如果传入的颜色值和指定点的颜色值相等，返回 True,否则返回 False。
    """
    # 将颜色值转换为 RGB 分量值
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    pixel_color = image[point[1], point[0]]
    # 比较颜色值
    if (
        abs(pixel_color[2] - r) <= tolerance
        and abs(pixel_color[1] - g) <= tolerance
        and abs(pixel_color[0] - b) <= tolerance
    ):
        return True
    else:
        return False


def get_color(image, point):
    """
    获取图像中指定位置的颜色值，并将其转换为 16 进制格式。

    参数：
    - image:图像 Mat格式
    - point [x,y] 坐标点

    返回值：
    - 该点的颜色值，格式为 "#RRGGBB"
    """
    # 获取指定点的颜色值（BGR 格式）
    pixel_color = image[point[1], point[0]]
    # 将 BGR 格式转换为 RGB 格式
    rgb_color = pixel_color[::-1]
    # 将 RGB 分量值转换为 16 进制格式
    hex_color = "#{:02X}{:02X}{:02X}".format(rgb_color[0], rgb_color[1], rgb_color[2])
    return hex_color


def find_color(image, color, region=None, tolerance=0):
    # 设置查找区域
    if region is not None:
        x_min, y_min, x_max, y_max = region
        image = image[y_min:y_max, x_min:x_max]
    for x in range(image.shape[1]):
        for y in range(image.shape[0]):
            # 将颜色值转换为 RGB 分量值
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            pixel_color = image[y, x]
            # 比较颜色值
            if (
                abs(pixel_color[2] - r) <= tolerance
                and abs(pixel_color[1] - g) <= tolerance
                and abs(pixel_color[0] - b) <= tolerance
            ):
                return x, y
    return None


def find_image(template_path, target_path, region=None, threshold=0.8,flag=cv2.IMREAD_COLOR):
    """灰度找图

    Args:
        params: 一个字典，包含以下参数：

            - template_path: 模板图像的路径/cv2格式

                - target_path: 目标图像的路径/cv2格式

                - region: 指定在目标图像中查找的区域,格式为(x_min, y_min, x_max, y_max),默认为None表示查找整张图片

                - threshold: 相似度的阈值,取值为0~1之间,默认为0

                - flag:图像读取方式

        Returns:
            一个包含4个元素的元组(x, y,w,h),表示查找到的最相似部分在目标图像中的左上角坐标,如果未找到则返回None
    """
    # 读取模板图像和目标图像
    template = (
        cv2.imread(template_path, flag)
        if isinstance(template_path, str)
        else template_path
    )

    target = (
        cv2.imread(target_path, flag) if isinstance(target_path, str) else target_path
    )
    # 设置查找区域
    if region is not None:
        x_min, y_min, x_max, y_max = region
        target = target[y_min:y_max, x_min:x_max]
    # 匹配模板图像
    res = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
    # 选择相似度最高的一个结果
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < threshold:
        return None
    # 转换坐标系
    if region is not None:
        max_loc = (max_loc[0] + x_min, max_loc[1] + y_min)
    # 返回匹配结果
    return [max_loc[0], max_loc[1], template.shape[1], template.shape[0]]


def find_image_color(
    template_path,
    target_path,
    region=None,
    threshold=0.8,
    is_color=False,
    color_threshold=30,
):
    """找图进阶含找色

    Args:
        template_path (_type_): _description_
        target_path (_type_): _description_
        region (_type_): _description_
        threshold (float, optional): _description_. Defaults to 0.8.
        is_color (bool, optional): _description_. Defaults to False.
        color_threshold (int, optional): _description_. Defaults to 30.

    Returns:
        _type_: _description_
    """
    flag = cv2.IMREAD_COLOR
    # 读取模板图像和目标图像
    template = (
        cv2.imread(template_path, flag)
        if isinstance(template_path, str)
        else template_path
    )

    target = (
        cv2.imread(target_path, flag) if isinstance(target_path, str) else target_path
    )

    res = find_image(template, target, region, threshold)

    if res:
        if is_color:
            if (
                find_color(
                    target,
                    get_color(template, [0, 0]),
                    [res[0], res[1], res[0] + 10, res[0] + 10],
                    color_threshold,
                )
                is None
            ):
                return None
        return res
    else:
        return None


def readImgArr(imgPathArr):
    """读取图像并返回cv2图像字典

    Args:
        imgPathArr (array): 图像路径数组

    Returns:
        dict: cv2图像字典
    """
    imgArr = {}
    for imgPath in imgPathArr:
        imgArr[imgPath.split("/")[-1].split(".")[0]] = cv2.imread(imgPath)
    return imgArr
