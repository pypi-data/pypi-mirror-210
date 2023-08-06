from .battle import *

class Loader:
    @staticmethod
    def img(path: str, size: tuple = ..., alpha: int = ..., ifConvertAlpha: bool = ...) -> ImageSurface: ...
    @staticmethod
    def static_image(path: str, _position: tuple = ..., size: tuple = ..., tag: str = ...) -> StaticImage: ...
    @staticmethod
    def movable_static_image(path: str, _position: tuple, target_position: tuple, move_speed: tuple, size: tuple, tag: str = ...) -> MovableStaticImage: ...
    @staticmethod
    def progress_bar_surface(img_on_top_path: str, img_on_bottom_path: str, _position: tuple[int, int], size: tuple[int, int], mode: Axis = ..., tag: str = ...) -> ProgressBarSurface: ...
    @staticmethod
    def gif(gif_path_or_img_list: str | Sequence, _position: tuple[int, int], size: tuple[int, int], updateGap: int = ...) -> AnimatedImage: ...
    @staticmethod
    def button(path: str, _position: tuple[int, int], size: tuple[int, int], alpha_when_not_hover: int = ...) -> Button: ...
    @staticmethod
    def text(txt: str | int, _color: color_liked, pos: tuple, size: int, ifBold: bool = ..., ifItalic: bool = ...) -> TextSurface: ...
    @staticmethod
    def resize_when_hovered_text(txt: str | int, _color: color_liked, pos: tuple[int, int], size: int, _bold: bool = ..., _italic: bool = ...) -> ResizeWhenHoveredTextSurface: ...
display = Display
lang = Lang
setting = Setting
info = Info
keys = Keys
config = Config
colors = Colors
global_variables = GlobalVariables
sounds = Sounds
music = Music
volume = Volume
media = Media
images = Images
controller = Controller
ui = UI
font = Font
position = Positions
coordinates = Coordinates
surfaces = Surfaces
debug = Debug
load = Loader
numbers = Numbers
saves = Saves
