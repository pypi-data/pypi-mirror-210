import ncnn
from ncnn.utils.objects import Detect_Object


class YoloV3_Base:
    def __init__(
        self,
        tiny,
        param_path,
        bin_path,
        class_names,
        num_threads=1,
        use_gpu=False,
    ):
        target_size = 416 if tiny else 608
        self.target_size = target_size
        self.num_threads = num_threads
        self.use_gpu = use_gpu

        self.mean_vals = []
        self.norm_vals = [1 / 255.0, 1 / 255.0, 1 / 255.0]

        self.net = ncnn.Net()
        self.net.opt.use_vulkan_compute = self.use_gpu
        self.net.opt.num_threads = self.num_threads

        self.net.load_param(param_path)
        self.net.load_model(bin_path)

        self.class_names = class_names

    def __del__(self):
        self.net = None

    def __call__(self, img):
        img_h = img.shape[0]
        img_w = img.shape[1]

        mat_in = ncnn.Mat.from_pixels_resize(
            img,
            ncnn.Mat.PixelType.PIXEL_BGR2RGB,
            img.shape[1],
            img.shape[0],
            self.target_size,
            self.target_size,
        )
        mat_in.substract_mean_normalize(self.mean_vals, self.norm_vals)

        ex = self.net.create_extractor()
        ex.input("data", mat_in)

        ret, mat_out = ex.extract("output")

        objects = []

        for i in range(mat_out.h):
            values = mat_out.row(i)

            obj = Detect_Object()
            obj.label = values[0]
            obj.prob = values[1]
            obj.rect.x = values[2] * img_w
            obj.rect.y = values[3] * img_h
            obj.rect.w = values[4] * img_w - obj.rect.x
            obj.rect.h = values[5] * img_h - obj.rect.y

            objects.append(obj)

        return objects


class YoloV3_Tiny(YoloV3_Base):
    def __init__(self, **kwargs):
        super(YoloV3_Tiny, self).__init__(tiny=True, **kwargs)


class YoloV3(YoloV3_Base):
    def __init__(self, **kwargs):
        super(YoloV3, self).__init__(tiny=False, **kwargs)


def yolo(class_name: str, class_names: list, objects: list, min_prob=0.0):
    """yolo识别结果筛选

    Args:
        class_name (str): 类名
        class_names (list): 类名列表
        objects (list): 识别结果
        min_prob (float, optional): 最小置信度. Defaults to 0.0.

    Returns:
        _type_: _description_
    """
    yoloResult = []
    for obj in objects:
        if obj.prob < min_prob:
            continue
        if class_names[int(obj.label)] == class_name:
            yoloResult.append(obj)
    return yoloResult


# if __name__ == "__main__":
#     img = cv2.imread("screenshotemulator-5554.png")
#     net = YoloV3(
#         param_path="yolov3-tiny_6700-opt.param",
#         bin_path="yolov3-tiny-opt.bin",
#         class_names=["", "exp", "hd", "jb"],
#         num_threads=4,
#         use_gpu=True,
#     )
#     yolo("exp",net.class_names,net(img),0.8)
#     draw_detection_objects(m, net.class_names, objects)
