from curses import window
import cv2


def display_image(window_name, img, top=True, wait=False):
    cv2.imshow(window_name, img)
    if top:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    if wait:
        cv2.waitKey(0)


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
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.putText(
        img,
        text,
        position,
        fontFace=font,
        fontScale=fontscale,
        color=color,
        thickness=thickness,
    )
    return img
