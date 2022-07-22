import math
import cv2
import numpy as np
import pickle
import os


def display_image(
    window_name,
    img,
    resize=(-1, -1),
    normalize=False,
    input_range=(None, None),
    top=True,
    wait=-1,
    event_func=None,
    cv_event_handler=None,
    event_params={},
    text=None,
    text_params=None,
):
    img = np.copy(img)
    if resize[0] >= 0 and resize[1] >= 0:
        img = cv2.resize(img, (resize[0], resize[1]))
    if normalize:
        if input_range[0] and input_range[1]:
            cv2.normalize(
                img,
                img,
                input_range[0],
                input_range[1],
                cv2.NORM_MINMAX,
            )
        else:
            cv2.normalize(img, img, cv2.NORM_MINMAX)

    if text:
        img = put_text(
            img, text, position=text_params["pos"], color=text_params["color"]
        )

    cv2.namedWindow(window_name)
    if top:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    if wait >= 0:
        k = cv2.waitKey(wait)
        if k == 27:
            cv2.destroyAllWindows()
        elif event_func:
            if k == ord("m"):
                event_func(event_params)
        else:
            cv2.destroyAllWindows()
    if cv_event_handler:
        cv2.setMouseCallback(window_name, cv_event_handler, param=event_params)
    cv2.imshow(window_name, img)


def put_text(
    img,
    text,
    position=(0, 0),
    color=(255, 255, 255),
    convert_image_color=False,
    font=cv2.FONT_HERSHEY_SIMPLEX,
    fontscale=0.55,
    thickness=2,
):
    """return image"""
    if convert_image_color and len(color) == 3:
        img = img.astype(np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.putText(
        img,
        str(text),
        position,
        fontFace=font,
        fontScale=fontscale,
        color=color,
        thickness=thickness,
    )
    return img


def normalize_point(x, min_x, max_x, min_target, max_target, return_boundary=False):
    # sometimes we may want to ignore extremes rather than
    # altering their value
    if return_boundary:
        if x > max_x:
            x = max_x
        if x < min_x:
            x = min_x

    x_norm = ((x - min_x) / (max_x - min_x)) * (max_target - min_target)
    return x_norm


def safe_log10(x, eps=1e-10):
    """
    protect against zero division edge cases
    this basically replaces 0 with extremely small val
    """
    result = np.where(x > eps, x, -10)
    np.log10(result, out=result, where=result > 0)
    return result


def compute_hu_moments(img):
    img = np.copy(img).astype(np.float32)
    moments = cv2.moments(img)
    hu_moments = cv2.HuMoments(moments).flatten()
    for i in range(0, 7):
        hu_moments[i] = (
            -1 * math.copysign(1.0, hu_moments[i]) * safe_log10(abs(hu_moments[i]))
        )
    return hu_moments


# write data to binary file
def write_data(location, data, name):
    # store list in binary file so 'wb' mode
    with open(os.path.join(location, name), "wb") as fp:
        pickle.dump(data, fp)
        print(f"Saved {name} to {location}")


# Read data to memory
def read_data(location, name):
    # for reading also binary mode is important
    with open(os.path.join(location, name), "rb") as fp:
        data = pickle.load(fp)
        return data
