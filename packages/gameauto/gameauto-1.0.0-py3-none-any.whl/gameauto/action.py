import random
import time
import numpy as np
from uiautomator2 import Device
from images import find_image, find_image_color
from utils import random_number, regionChange

class MiniDevices(Device):
    def __init__(self,serial) -> None:
        super().__init__(serial)
    
    #截图
    def miniCaptureScreen(self):
        return super().screenshot(format="opencv")

    #点击
    def miniPress(self, x: int, y: int, duration: int = 500):
        return super().long_click(x, y, duration/1000)
        
    #滑动
    def miniSwipe(self, points, duration: int = 500):
        """滑动

        Args:
            points (list): [(x0, y0), (x1, y1), (x2, y2)]
            duration (float, optional): _description_. Defaults to 0.5.

        Returns:
            _type_: _description_
        """
        return super().swipe_points(points, duration/1000)
    
    #找图
    def miniFindImage(
        self,
        template_path,
        target_path,
        region=None,
        threshold=0.8,
        is_color=False,
        color_threshold=30,
        is_click=False,
    ):
        if is_color:
            res = find_image_color(
                template_path, target_path, region, threshold, True, color_threshold
            )
        else:
            res = find_image(template_path, target_path, region, threshold)

        if res:
            if is_click:
                self.miniRandomClick(regionChange(res))
            return True
        else:
            return False
        
    #随机点击
    def miniRandomClick(self, region, point=None, method=1):
        """随机点击

        Args:
            region (array): [x_min, y_min, x_max, y_max]
            point (tuple, optional): 坐标点. Defaults to None.
            method (int, optional): 1:范围随机点击需传入region 2:定点点击. Defaults to 1.
        """
        p = [0, 0]
        if region != None:
            p[0], p[1] = random_number(region)

        if method == 2 and point != None:
            p[0], p[1] = point
            self.miniPress(p[0], p[1], random.randint(80, 150))
        else:
            i = abs(np.random.normal(0, 30))
            if i > 90:
                self.miniSmlMove(
                    p[0],
                    p[1],
                    p[0] + random.randint(0, 3),
                    p[1] + random.randint(0, 3),
                    time=random.randint(200, 350),
                )
            elif i > 60:
                self.miniPress(p[0], p[1], random.randint(300, 600))
            else:
                self.miniPress(p[0], p[1], random.randint(80, 150))

        time.sleep(random.randint(80, 120) / 1000)

    #曲线滑动
    def miniSmlMove(self, qx, qy, zx, zy, time=500):
        slidingPath = []
        point = [
            {"x": qx, "y": qy},
            {"x": random.randint(qx - 100, qx + 100), "y": random.randint(qy, qy + 50)},
            {"x": random.randint(zx - 100, zx + 100), "y": random.randint(zy, zy + 50)},
            {"x": zx, "y": zy},
        ]
        cx = 3.0 * (point[1]["x"] - point[0]["x"])
        bx = 3.0 * (point[2]["x"] - point[1]["x"]) - cx
        ax = point[3]["x"] - point[0]["x"] - cx - bx
        cy = 3.0 * (point[1]["y"] - point[0]["y"])
        by = 3.0 * (point[2]["y"] - point[1]["y"]) - cy
        ay = point[3]["y"] - point[0]["y"] - cy - by
        t_values = np.arange(0, 1, 0.08)
        t_squared = t_values * t_values
        t_cubed = t_squared * t_values
        x_values = ax * t_cubed + bx * t_squared + cx * t_values + point[0]["x"]
        y_values = ay * t_cubed + by * t_squared + cy * t_values + point[0]["y"]
        slidingPath.extend([(int(x), int(y)) for x, y in zip(x_values, y_values)])
        self.miniSwipe(slidingPath, duration=time)


if __name__=="__main__":
    g = MiniDevices("emulator-5554")
    # img=cv2.imread(r"C:\Users\alex\Desktop\autoyys\c.jpg")
    # res=find_image(r"C:\Users\alex\Desktop\autoyys\hello.jpg",img)
    # print(res)
    # cv2.imshow("",g.screenshot(format="opencv"))
    # cv2.waitKey()
    # g.miniFindImage(r"C:\Users\alex\Desktop\autoyys\hello.jpg",g.screenshot(format="opencv"),is_click=True)
    