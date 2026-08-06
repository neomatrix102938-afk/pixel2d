import math
import random
import sys
from array import array
from pathlib import Path
from dataclasses import dataclass
from enum import Enum, auto
from typing import Iterable

import pygame


# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
FPS = 60

PLAYER_SPEED = 280.0
GRAVITY = 1800.0
JUMP_SPEED = 650.0
MAX_FALL_SPEED = 1000.0
COYOTE_TIME = 0.10

COLOR_WHITE = (245, 247, 250)
COLOR_BLACK = (20, 24, 32)
COLOR_RED = (225, 73, 73)
COLOR_GOLD = (255, 205, 65)
COLOR_BLUE = (61, 139, 255)
COLOR_DARK_BLUE = (34, 62, 112)
COLOR_GREEN = (74, 176, 91)
COLOR_DARK_GREEN = (38, 108, 58)
COLOR_PURPLE = (148, 85, 211)
COLOR_GRAY = (105, 116, 135)
COLOR_DARK_GRAY = (52, 59, 72)
COLOR_ORANGE = (235, 133, 54)
COLOR_DARK_ORANGE = (145, 69, 29)

COLOR_BLOOD = (148, 0, 18)
COLOR_BRIGHT_BLOOD = (235, 20, 35)
COLOR_DARK_BLOOD = (62, 0, 9)
COLOR_BONE = (224, 215, 188)

DIFFICULTIES = ("Easy", "Normal", "Hard")
DIFFICULTY_SPEED = {"Easy": 0.72, "Normal": 1.0, "Hard": 1.35}
HORROR_MUSIC_FILENAME = "leberch-creepy-511957.mp3"
NORMAL_MUSIC_FILENAME = "sigmamusicart-happy-happy-kids-music-537737.mp3"
DEATH_SCREAM_FILENAME = "universfield-man-pain-scream-567203.mp3"
NORMAL_DEATH_FILENAME = "drummusiclooper5000-lose-sfx-365579.mp3"
HORROR_MUSIC_VOLUME_FACTOR = 0.55
NORMAL_MUSIC_VOLUME_FACTOR = 0.48
DEATH_SCREAM_VOLUME_FACTOR = 0.85
NORMAL_DEATH_VOLUME_FACTOR = 0.90
NORMAL_WINDOW_TITLE = "Pixel Platformer"
HORROR_WINDOW_TITLE = "HELP ME"


def asset_path(filename: str) -> Path:
    """Return an asset path that works normally and in a PyInstaller build."""
    bundle_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return bundle_dir / filename


class GameState(Enum):
    MAIN_MENU = auto()
    SETTINGS = auto()
    PLAYING = auto()
    PAUSED = auto()
    VICTORY = auto()


@dataclass(frozen=True)
class LevelData:
    name: str
    background: tuple[int, int, int]
    spawn: tuple[int, int]
    platforms: tuple[tuple[int, int, int, int], ...]
    spikes: tuple[tuple[int, int], ...]
    coins: tuple[tuple[int, int], ...]
    goal: tuple[int, int]
    # x, y, left patrol limit, right patrol limit, base speed
    enemies: tuple[tuple[int, int, int, int, float], ...]


LEVELS = (
    LevelData(
        name="Green Steps",
        background=(126, 208, 255),
        spawn=(45, 500),
        platforms=(
            (0, 560, 960, 40),
            (100, 485, 190, 24),
            (355, 425, 170, 24),
            (585, 355, 170, 24),
            (350, 285, 160, 24),
            (100, 215, 170, 24),
            (400, 205, 170, 24),
            (665, 180, 190, 24),
        ),
        spikes=((300, 528), (540, 528), (755, 323)),
        coins=((185, 435), (440, 375), (665, 300), (430, 235), (180, 165), (485, 155)),
        goal=(790, 132),
        enemies=(
            (390, 532, 340, 500, 95.0),
            (125, 457, 110, 250, 80.0),
            (610, 327, 595, 710, 90.0),
        ),
    ),
    LevelData(
        name="Broken Bridge",
        background=(255, 184, 126),
        spawn=(35, 500),
        platforms=(
            (0, 560, 150, 40),
            (220, 520, 145, 24),
            (430, 470, 145, 24),
            (655, 520, 125, 24),
            (835, 455, 125, 24),
            (690, 365, 120, 24),
            (490, 305, 135, 24),
            (275, 245, 135, 24),
            (65, 185, 145, 24),
        ),
        spikes=((255, 488), (465, 438), (690, 488), (870, 423), (530, 273)),
        coins=((330, 465), (545, 415), (755, 465), (935, 400), (790, 310), (600, 250), (340, 190)),
        goal=(115, 137),
        enemies=(
            (235, 492, 225, 320, 105.0),
            (450, 442, 440, 535, 110.0),
            (705, 337, 700, 765, 100.0),
            (85, 157, 75, 165, 115.0),
        ),
    ),
    LevelData(
        name="Skyline",
        background=(111, 104, 184),
        spawn=(35, 505),
        platforms=(
            (0, 560, 150, 40),
            (185, 510, 145, 22),
            (365, 455, 140, 22),
            (540, 395, 145, 22),
            (720, 455, 150, 22),
            (810, 355, 135, 22),
            (635, 285, 140, 22),
            (450, 220, 140, 22),
            (255, 155, 140, 22),
            (65, 95, 145, 22),
        ),
        spikes=(
            (155, 528),
            (470, 423),
            (790, 423),
            (350, 123),
        ),
        coins=(
            (310, 455),
            (410, 400),
            (660, 340),
            (750, 400),
            (925, 300),
            (755, 230),
            (570, 165),
            (315, 100),
        ),
        goal=(110, 47),
        enemies=(
            (205, 482, 195, 260, 105.0),
            (560, 367, 550, 620, 112.0),
            (835, 327, 825, 890, 115.0),
            (660, 257, 650, 715, 108.0),
            (470, 192, 460, 525, 112.0),
        ),
    ),
    LevelData(
        name="Spike Cavern",
        background=(60, 50, 70),
        spawn=(40, 500),
        platforms=(
            (0, 560, 160, 40),
            (220, 510, 160, 22),
            (440, 460, 160, 22),
            (660, 410, 160, 22),
            (820, 310, 140, 22),
            (580, 260, 170, 22),
            (340, 200, 170, 22),
            (100, 140, 180, 22),
        ),
        spikes=(
            (270, 478),
            (490, 428),
            (710, 378),
            (620, 228),
            (380, 168),
        ),
        coins=(
            (110, 490),
            (300, 440),
            (520, 390),
            (740, 340),
            (880, 240),
            (660, 190),
            (420, 130),
            (200, 80),
        ),
        goal=(120, 92),
        enemies=(
            (230, 482, 225, 340, 110.0),
            (450, 432, 445, 560, 115.0),
            (670, 382, 665, 780, 120.0),
            (590, 232, 585, 710, 125.0),
        ),
    ),
    LevelData(
        name="The Citadel",
        background=(45, 35, 55),
        spawn=(40, 500),
        platforms=(
            (0, 560, 140, 40),
            (180, 490, 150, 22),
            (370, 430, 160, 22),
            (570, 370, 160, 22),
            (770, 310, 150, 22),
            (550, 230, 170, 22),
            (310, 180, 170, 22),
            (70, 120, 170, 22),
            (770, 140, 170, 22),
        ),
        spikes=(
            (220, 458),
            (410, 398),
            (610, 338),
            (810, 278),
            (590, 198),
            (350, 148),
        ),
        coins=(
            (250, 430),
            (440, 370),
            (640, 310),
            (840, 250),
            (620, 170),
            (380, 120),
            (140, 60),
            (870, 50),
        ),
        goal=(850, 62),
        enemies=(
            (190, 462, 185, 280, 120.0),
            (380, 402, 375, 480, 125.0),
            (580, 342, 575, 680, 130.0),
            (780, 282, 775, 880, 135.0),
            (560, 202, 555, 680, 140.0),
            (80, 92, 75, 180, 145.0),
        ),
    ),
)


class SoundBank:
    """Tiny generated sound effects, so the game needs no asset files."""

    def __init__(self) -> None:
        self.enabled = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self.sounds = {
                "jump": self._tone(520, 0.08, 0.22),
                "coin": self._tone(880, 0.09, 0.24),
                "hit": self._tone(125, 0.16, 0.30),
                "cry": self._cry(0.72, 0.34),
                "stomp": self._tone(245, 0.08, 0.28),
                "goal": self._tone(660, 0.18, 0.24),
                "menu": self._tone(390, 0.04, 0.16),
            }

            scream_path = asset_path(DEATH_SCREAM_FILENAME)
            if scream_path.is_file():
                try:
                    self.sounds["scream"] = pygame.mixer.Sound(str(scream_path))
                except (pygame.error, OSError):
                    pass

            normal_death_path = asset_path(NORMAL_DEATH_FILENAME)
            if normal_death_path.is_file():
                try:
                    self.sounds["normal_death"] = pygame.mixer.Sound(
                        str(normal_death_path)
                    )
                except (pygame.error, OSError):
                    pass

            self.enabled = True
        except pygame.error:
            self.enabled = False

    @staticmethod
    def _tone(frequency: float, duration: float, amplitude: float) -> pygame.mixer.Sound:
        sample_rate = 22050
        sample_count = int(sample_rate * duration)
        samples = array("h")
        for index in range(sample_count):
            envelope = max(0.0, 1.0 - index / sample_count)
            value = math.sin(2.0 * math.pi * frequency * index / sample_rate)
            samples.append(int(32767 * amplitude * envelope * value))
        return pygame.mixer.Sound(buffer=samples.tobytes())

    @staticmethod
    def _cry(duration: float, amplitude: float) -> pygame.mixer.Sound:
        """Generate a short, eerie descending cry without an external file."""
        sample_rate = 22050
        sample_count = int(sample_rate * duration)
        samples = array("h")
        rng = random.Random(731)
        phase = 0.0

        for index in range(sample_count):
            t = index / sample_rate
            progress = index / max(1, sample_count - 1)
            frequency = 470.0 * (1.0 - progress) + 105.0
            frequency += math.sin(t * 43.0) * 24.0
            phase += 2.0 * math.pi * frequency / sample_rate

            attack = min(1.0, progress * 16.0)
            release = max(0.0, 1.0 - progress) ** 1.45
            tremolo = 0.76 + 0.24 * math.sin(t * 31.0)
            voice = math.sin(phase) + 0.35 * math.sin(phase * 2.03)
            breath = rng.uniform(-1.0, 1.0) * 0.13
            value = (voice * 0.62 + breath) * attack * release * tremolo
            samples.append(int(32767 * amplitude * max(-1.0, min(1.0, value))))

        return pygame.mixer.Sound(buffer=samples.tobytes())

    def play(self, name: str, volume: float) -> None:
        if not self.enabled or name not in self.sounds or volume <= 0:
            return
        sound = self.sounds[name]
        sound.set_volume(max(0.0, min(1.0, volume)))
        sound.play()


@dataclass
class BloodParticle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    life: float
    size: int

    def update(self, dt: float) -> None:
        self.velocity.y += 900.0 * dt
        self.position += self.velocity * dt
        self.life -= dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.life <= 0:
            return
        radius = max(1, round(self.size * min(1.0, self.life * 2.2)))
        pygame.draw.circle(
            surface,
            COLOR_BRIGHT_BLOOD,
            (round(self.position.x), round(self.position.y)),
            radius,
        )


class Platform(pygame.sprite.Sprite):
    def __init__(self, rect: tuple[int, int, int, int], horror: bool = False):
        super().__init__()
        x, y, width, height = rect
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        if horror:
            self.image.fill((73, 12, 18))
            pygame.draw.rect(self.image, COLOR_DARK_BLOOD, (0, height - 7, width, 7))
            pygame.draw.line(self.image, COLOR_BRIGHT_BLOOD, (0, 3), (width, 3), 3)
            for px in range(12, width, 36):
                drip_height = 5 + (px * 7) % max(6, height - 5)
                pygame.draw.rect(self.image, COLOR_BLOOD, (px, 3, 5, drip_height))
                pygame.draw.circle(self.image, COLOR_BLOOD, (px + 2, drip_height + 3), 3)
        else:
            self.image.fill(COLOR_GREEN)
            pygame.draw.rect(self.image, COLOR_DARK_GREEN, (0, height - 6, width, 6))
            for px in range(8, width, 24):
                pygame.draw.rect(self.image, (98, 202, 111), (px, 5, 12, 5))
        self.rect = self.image.get_rect(topleft=(x, y))


class Spike(pygame.sprite.Sprite):
    SIZE = 32

    def __init__(self, x: int, y: int, horror: bool = False):
        super().__init__()
        self.image = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        main_color = COLOR_BONE if horror else COLOR_RED
        highlight = COLOR_BRIGHT_BLOOD if horror else (255, 140, 140)
        pygame.draw.polygon(
            self.image,
            main_color,
            ((2, self.SIZE), (self.SIZE // 2, 2), (self.SIZE - 2, self.SIZE)),
        )
        pygame.draw.polygon(
            self.image,
            highlight,
            ((8, self.SIZE - 5), (self.SIZE // 2, 8), (self.SIZE // 2, self.SIZE - 5)),
        )
        if horror:
            pygame.draw.circle(self.image, COLOR_BLOOD, (self.SIZE // 2, 18), 5)
            pygame.draw.line(self.image, COLOR_BLOOD, (self.SIZE // 2, 18), (18, 31), 3)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = pygame.Rect(x + 6, y + 10, self.SIZE - 12, self.SIZE - 10)


class Coin(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, horror: bool = False):
        super().__init__()
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        if horror:
            pygame.draw.circle(self.image, COLOR_DARK_BLOOD, (11, 11), 10)
            pygame.draw.circle(self.image, COLOR_BRIGHT_BLOOD, (11, 11), 8, 2)
            pygame.draw.circle(self.image, COLOR_WHITE, (8, 9), 2)
            pygame.draw.circle(self.image, COLOR_WHITE, (14, 9), 2)
            pygame.draw.line(self.image, COLOR_BRIGHT_BLOOD, (7, 15), (15, 15), 2)
        else:
            pygame.draw.circle(self.image, COLOR_GOLD, (11, 11), 10)
            pygame.draw.circle(self.image, (255, 235, 130), (8, 8), 4)
            pygame.draw.circle(self.image, (188, 131, 20), (11, 11), 10, 2)
        self.rect = self.image.get_rect(center=(x, y))


class Goal(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, horror: bool = False):
        super().__init__()
        self.image = pygame.Surface((42, 50), pygame.SRCALPHA)
        pole_color = COLOR_BONE if horror else COLOR_WHITE
        flag_color = COLOR_BLOOD if horror else COLOR_PURPLE
        pygame.draw.rect(self.image, pole_color, (5, 3, 4, 44))
        pygame.draw.polygon(self.image, flag_color, ((9, 5), (38, 14), (9, 25)))
        if horror:
            pygame.draw.circle(self.image, COLOR_BRIGHT_BLOOD, (20, 13), 3)
            pygame.draw.line(self.image, COLOR_BRIGHT_BLOOD, (20, 13), (20, 24), 2)
        pygame.draw.rect(self.image, COLOR_DARK_GRAY, (0, 46, 18, 4))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface: pygame.Surface, active: bool) -> None:
        image = self.image.copy()
        if not active:
            veil = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            veil.fill((40, 40, 40, 150))
            image.blit(veil, (0, 0))
        surface.blit(image, self.rect)


class Enemy(pygame.sprite.Sprite):
    WIDTH = 30
    HEIGHT = 28

    def __init__(
        self,
        x: int,
        y: int,
        left_limit: int,
        right_limit: int,
        speed: float,
        horror: bool = False,
    ) -> None:
        super().__init__()
        self.image_right = self._build_image(horror)
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(topleft=(x, y))
        self.position_x = float(x)
        self.left_limit = left_limit
        self.right_limit = right_limit
        self.base_speed = speed
        self.direction = 1

    @classmethod
    def _build_image(cls, horror: bool = False) -> pygame.Surface:
        image = pygame.Surface((cls.WIDTH, cls.HEIGHT), pygame.SRCALPHA)
        body = COLOR_BLOOD if horror else COLOR_ORANGE
        shadow = COLOR_DARK_BLOOD if horror else COLOR_DARK_ORANGE
        pygame.draw.rect(image, body, (2, 5, 26, 19), border_radius=6)
        pygame.draw.rect(image, shadow, (2, 19, 26, 5), border_radius=2)
        pygame.draw.polygon(image, body, ((6, 7), (9, 0), (13, 7)))
        pygame.draw.polygon(image, body, ((18, 7), (22, 0), (25, 8)))
        pygame.draw.rect(image, COLOR_WHITE, (16, 10, 6, 5))
        pygame.draw.rect(image, COLOR_BRIGHT_BLOOD if horror else COLOR_BLACK, (20, 11, 2, 3))
        if horror:
            pygame.draw.line(image, COLOR_BONE, (7, 14), (12, 17), 2)
            pygame.draw.line(image, COLOR_BONE, (12, 17), (7, 20), 2)
        pygame.draw.rect(image, COLOR_DARK_GRAY, (5, 24, 7, 4))
        pygame.draw.rect(image, COLOR_DARK_GRAY, (18, 24, 7, 4))
        return image

    @property
    def hitbox(self) -> pygame.Rect:
        return self.rect.inflate(-6, -4)

    def update(self, dt: float, difficulty_multiplier: float) -> None:
        self.position_x += self.direction * self.base_speed * difficulty_multiplier * dt

        if self.position_x <= self.left_limit:
            self.position_x = float(self.left_limit)
            self.direction = 1
        elif self.position_x >= self.right_limit:
            self.position_x = float(self.right_limit)
            self.direction = -1

        self.rect.x = round(self.position_x)
        self.image = self.image_right if self.direction > 0 else self.image_left


class Player(pygame.sprite.Sprite):
    WIDTH = 28
    HEIGHT = 34

    def __init__(self, spawn: tuple[int, int], horror: bool = False):
        super().__init__()
        self.horror = horror
        self.image_right = self._build_image(horror)
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right
        self.rect = self.image.get_rect(topleft=spawn)
        self.position = pygame.Vector2(self.rect.topleft)
        self.velocity = pygame.Vector2(0, 0)
        self.on_ground = False
        self.coyote_timer = 0.0
        self.facing_right = True

    @classmethod
    def _build_image(cls, horror: bool = False) -> pygame.Surface:
        image = pygame.Surface((cls.WIDTH, cls.HEIGHT), pygame.SRCALPHA)
        body = (92, 92, 105) if horror else COLOR_BLUE
        lower = COLOR_DARK_BLOOD if horror else COLOR_DARK_BLUE
        pygame.draw.rect(image, body, (3, 4, 22, 25), border_radius=4)
        pygame.draw.rect(image, lower, (3, 24, 22, 5))
        pygame.draw.rect(image, COLOR_WHITE, (16, 9, 5, 5))
        pygame.draw.rect(image, COLOR_BRIGHT_BLOOD if horror else COLOR_BLACK, (19, 10, 2, 3))
        pygame.draw.rect(image, COLOR_BLACK, (8, 19, 12, 2))
        if horror:
            pygame.draw.circle(image, COLOR_BLOOD, (8, 11), 4)
            pygame.draw.line(image, COLOR_BRIGHT_BLOOD, (9, 12), (13, 26), 3)
            pygame.draw.circle(image, COLOR_BLOOD, (19, 22), 3)
        pygame.draw.rect(image, COLOR_DARK_GRAY, (5, 29, 7, 5))
        pygame.draw.rect(image, COLOR_DARK_GRAY, (17, 29, 7, 5))
        return image

    def set_horror(self, horror: bool) -> None:
        self.horror = horror
        self.image_right = self._build_image(horror)
        self.image_left = pygame.transform.flip(self.image_right, True, False)
        self.image = self.image_right if self.facing_right else self.image_left

    def reset(self, spawn: tuple[int, int]) -> None:
        self.position.update(spawn)
        self.rect.topleft = spawn
        self.velocity.update(0, 0)
        self.on_ground = False
        self.coyote_timer = 0.0

    def bounce(self, y: int) -> None:
        self.rect.bottom = y
        self.position.y = float(self.rect.y)
        self.velocity.y = -JUMP_SPEED * 0.58
        self.on_ground = False
        self.coyote_timer = 0.0

    def update(
        self,
        dt: float,
        move_direction: int,
        jump_pressed: bool,
        platforms: Iterable[Platform],
    ) -> bool:
        jumped = False
        self.velocity.x = move_direction * PLAYER_SPEED

        if move_direction:
            self.facing_right = move_direction > 0
            self.image = self.image_right if self.facing_right else self.image_left

        if self.on_ground:
            self.coyote_timer = COYOTE_TIME
        else:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)

        if jump_pressed and self.coyote_timer > 0:
            self.velocity.y = -JUMP_SPEED
            self.on_ground = False
            self.coyote_timer = 0.0
            jumped = True

        self.velocity.y = min(self.velocity.y + GRAVITY * dt, MAX_FALL_SPEED)

        self._move_horizontal(dt, platforms)
        self._move_vertical(dt, platforms)
        return jumped

    def _move_horizontal(self, dt: float, platforms: Iterable[Platform]) -> None:
        self.position.x += self.velocity.x * dt
        self.rect.x = round(self.position.x)

        for platform in platforms:
            if not self.rect.colliderect(platform.rect):
                continue
            if self.velocity.x > 0:
                self.rect.right = platform.rect.left
            elif self.velocity.x < 0:
                self.rect.left = platform.rect.right
            self.position.x = float(self.rect.x)

    def _move_vertical(self, dt: float, platforms: Iterable[Platform]) -> None:
        self.position.y += self.velocity.y * dt
        self.rect.y = round(self.position.y)
        self.on_ground = False

        for platform in platforms:
            if not self.rect.colliderect(platform.rect):
                continue
            if self.velocity.y > 0:
                self.rect.bottom = platform.rect.top
                self.on_ground = True
            elif self.velocity.y < 0:
                self.rect.top = platform.rect.bottom
            self.position.y = float(self.rect.y)
            self.velocity.y = 0


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(NORMAL_WINDOW_TITLE)

        self.fullscreen = False
        self.windowed_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.display = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 34)
        self.small_font = pygame.font.Font(None, 24)
        self.menu_font = pygame.font.Font(None, 42)
        self.title_font = pygame.font.Font(None, 68)

        self.sound = SoundBank()
        self.volume = 0.65
        self.difficulty = "Normal"
        self.horror_mode = False
        self.music_paths = {
            "normal": asset_path(NORMAL_MUSIC_FILENAME),
            "horror": asset_path(HORROR_MUSIC_FILENAME),
        }
        self.music_available = {
            name: path.is_file() for name, path in self.music_paths.items()
        }
        self.music_errors: dict[str, str] = {}
        self.current_music_mode: str | None = None

        self.state = GameState.MAIN_MENU
        self.settings_return_state = GameState.MAIN_MENU
        self.menu_index = 0
        self.settings_index = 0
        self.pause_index = 0
        self.victory_index = 0

        self.level_index = 0
        self.score = 0
        self.deaths = 0
        self.death_timer = 0.0
        self.blood_particles: list[BloodParticle] = []
        self.player = Player(LEVELS[0].spawn, horror=self.horror_mode)
        self.load_level(0)

    def sync_background_music(self) -> None:
        desired_mode = "horror" if self.horror_mode else "normal"
        factor = (
            HORROR_MUSIC_VOLUME_FACTOR
            if self.horror_mode
            else NORMAL_MUSIC_VOLUME_FACTOR
        )
        music_volume = max(0.0, min(1.0, self.volume * factor))

        if not pygame.mixer.get_init():
            return

        pygame.mixer.music.set_volume(music_volume)

        if music_volume <= 0.0:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(250)
            return

        if not self.music_available.get(desired_mode, False):
            if self.current_music_mode != desired_mode:
                pygame.mixer.music.stop()
                self.current_music_mode = None
            return

        if self.current_music_mode != desired_mode:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.load(str(self.music_paths[desired_mode]))
                pygame.mixer.music.set_volume(music_volume)
                pygame.mixer.music.play(-1, fade_ms=650)
                self.current_music_mode = desired_mode
                self.music_errors.pop(desired_mode, None)
            except (pygame.error, OSError) as exc:
                self.music_available[desired_mode] = False
                self.music_errors[desired_mode] = str(exc)
                self.current_music_mode = None
            return

        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.play(-1, fade_ms=350)
            except pygame.error as exc:
                self.music_errors[desired_mode] = str(exc)

    def update_window_title(self) -> None:
        title = HORROR_WINDOW_TITLE if self.horror_mode else NORMAL_WINDOW_TITLE
        pygame.display.set_caption(title)

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)

    def _present(self) -> None:
        display_width, display_height = self.display.get_size()
        scale = min(display_width / SCREEN_WIDTH, display_height / SCREEN_HEIGHT)
        scaled_size = (
            max(1, round(SCREEN_WIDTH * scale)),
            max(1, round(SCREEN_HEIGHT * scale)),
        )
        offset_x = (display_width - scaled_size[0]) // 2
        offset_y = (display_height - scaled_size[1]) // 2

        self.display.fill(COLOR_BLACK)
        if scaled_size == (SCREEN_WIDTH, SCREEN_HEIGHT):
            scaled = self.screen
        else:
            scaled = pygame.transform.smoothscale(self.screen, scaled_size)
        self.display.blit(scaled, (offset_x, offset_y))
        pygame.display.flip()

    def _mouse_to_canvas(self, position: tuple[int, int]) -> tuple[int, int] | None:
        display_width, display_height = self.display.get_size()
        scale = min(display_width / SCREEN_WIDTH, display_height / SCREEN_HEIGHT)
        scaled_width = SCREEN_WIDTH * scale
        scaled_height = SCREEN_HEIGHT * scale
        offset_x = (display_width - scaled_width) / 2
        offset_y = (display_height - scaled_height) / 2

        x = (position[0] - offset_x) / scale
        y = (position[1] - offset_y) / scale
        if not (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
            return None
        return round(x), round(y)

    def start_new_game(self) -> None:
        self.score = 0
        self.deaths = 0
        self.load_level(0)
        self.state = GameState.PLAYING

    def load_level(self, index: int) -> None:
        self.level_index = index
        data = LEVELS[index]
        self.platforms = pygame.sprite.Group(
            Platform(rect, self.horror_mode) for rect in data.platforms
        )
        self.spikes = pygame.sprite.Group(
            Spike(x, y, self.horror_mode) for x, y in data.spikes
        )
        self.coins = pygame.sprite.Group(
            Coin(x, y, self.horror_mode) for x, y in data.coins
        )
        self.enemies = pygame.sprite.Group(
            Enemy(x, y, left, right, speed, self.horror_mode)
            for x, y, left, right, speed in data.enemies
        )
        self.goal = Goal(*data.goal, horror=self.horror_mode)
        self.player.set_horror(self.horror_mode)
        self.player.reset(data.spawn)
        self.blood_particles.clear()
        self.death_timer = 0.0

    def apply_horror_theme(self) -> None:
        data = LEVELS[self.level_index]
        coin_positions = [coin.rect.center for coin in self.coins]
        enemy_states = [
            (
                enemy.position_x,
                enemy.rect.y,
                enemy.left_limit,
                enemy.right_limit,
                enemy.base_speed,
                enemy.direction,
            )
            for enemy in self.enemies
        ]

        self.platforms = pygame.sprite.Group(
            Platform(rect, self.horror_mode) for rect in data.platforms
        )
        self.spikes = pygame.sprite.Group(
            Spike(x, y, self.horror_mode) for x, y in data.spikes
        )
        self.coins = pygame.sprite.Group(
            Coin(x, y, self.horror_mode) for x, y in coin_positions
        )
        rebuilt_enemies = pygame.sprite.Group()
        for x, y, left, right, speed, direction in enemy_states:
            enemy = Enemy(round(x), y, left, right, speed, self.horror_mode)
            enemy.position_x = x
            enemy.rect.x = round(x)
            enemy.direction = direction
            enemy.image = enemy.image_right if direction > 0 else enemy.image_left
            rebuilt_enemies.add(enemy)
        self.enemies = rebuilt_enemies
        self.goal = Goal(*data.goal, horror=self.horror_mode)
        self.player.set_horror(self.horror_mode)

    def restart_level(self, penalize: bool = False) -> None:
        if penalize:
            self.deaths += 1
            penalty = 5 if self.difficulty == "Easy" else 15
            self.score = max(0, self.score - penalty)
            if self.horror_mode:
                death_sound = "scream" if "scream" in self.sound.sounds else "cry"
                self.sound.play(
                    death_sound,
                    self.volume * DEATH_SCREAM_VOLUME_FACTOR,
                )
                self.start_blood_burst(self.player.rect.center)
                self.death_timer = 0.72
                return
            normal_death_sound = (
                "normal_death"
                if "normal_death" in self.sound.sounds
                else "hit"
            )
            self.sound.play(
                normal_death_sound,
                self.volume * NORMAL_DEATH_VOLUME_FACTOR,
            )
        self.load_level(self.level_index)

    def start_blood_burst(self, position: tuple[int, int]) -> None:
        self.spawn_blood(position, 42, clear_existing=True)

    def spawn_blood(
        self,
        position: tuple[int, int],
        count: int,
        clear_existing: bool = False,
    ) -> None:
        rng = random.Random(self.deaths * 101 + self.level_index * 37)
        if clear_existing:
            self.blood_particles.clear()
        for _ in range(count):
            angle = rng.uniform(math.pi * 1.05, math.pi * 1.95)
            speed = rng.uniform(110.0, 410.0)
            velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            velocity.y -= rng.uniform(20.0, 180.0)
            self.blood_particles.append(
                BloodParticle(
                    pygame.Vector2(position),
                    velocity,
                    rng.uniform(0.35, 0.85),
                    rng.randint(2, 6),
                )
            )

    def update_blood_particles(self, dt: float) -> None:
        for particle in self.blood_particles:
            particle.update(dt)
        self.blood_particles = [p for p in self.blood_particles if p.life > 0]

    def update_death_effect(self, dt: float) -> None:
        self.death_timer = max(0.0, self.death_timer - dt)
        self.update_blood_particles(dt)
        if self.death_timer <= 0:
            self.load_level(self.level_index)

    def advance_level(self) -> None:
        self.score += 100
        self.sound.play("goal", self.volume)
        if self.level_index + 1 < len(LEVELS):
            self.load_level(self.level_index + 1)
        else:
            self.state = GameState.VICTORY
            self.victory_index = 0

    def run(self) -> None:
        running = True
        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)
            jump_pressed = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.windowed_size = (max(640, event.w), max(400, event.h))
                    self.display = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11 or (
                        event.key == pygame.K_RETURN
                        and bool(event.mod & pygame.KMOD_ALT)
                    ):
                        self.toggle_fullscreen()
                        continue

                if self.state == GameState.MAIN_MENU:
                    running = self.handle_main_menu_event(event)
                elif self.state == GameState.SETTINGS:
                    self.handle_settings_event(event)
                elif self.state == GameState.PLAYING:
                    jump_pressed = self.handle_playing_event(event) or jump_pressed
                elif self.state == GameState.PAUSED:
                    running = self.handle_pause_event(event)
                elif self.state == GameState.VICTORY:
                    running = self.handle_victory_event(event)

            if not running:
                break

            self.sync_background_music()

            if self.state == GameState.PLAYING:
                if self.death_timer > 0:
                    self.update_death_effect(dt)
                else:
                    keys = pygame.key.get_pressed()
                    move_direction = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(
                        keys[pygame.K_LEFT] or keys[pygame.K_a]
                    )
                    jumped = self.player.update(
                        dt,
                        move_direction,
                        jump_pressed,
                        self.platforms,
                    )
                    if jumped:
                        self.sound.play("jump", self.volume)

                    self.enemies.update(dt, DIFFICULTY_SPEED[self.difficulty])
                    self.handle_collisions()
                    if self.death_timer <= 0:
                        self.update_blood_particles(dt)

            self.draw()
            self._present()

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()

    def handle_main_menu_event(self, event: pygame.event.Event) -> bool:
        options = ("Play", "Settings", "Quit")
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_index = (self.menu_index - 1) % len(options)
                self.sound.play("menu", self.volume)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_index = (self.menu_index + 1) % len(options)
                self.sound.play("menu", self.volume)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.activate_main_menu_option()
            elif event.key == pygame.K_ESCAPE:
                return False
        elif event.type == pygame.MOUSEMOTION:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                hovered = self.menu_option_at(canvas_pos, options, 300)
                if hovered is not None:
                    self.menu_index = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                clicked = self.menu_option_at(canvas_pos, options, 300)
                if clicked is not None:
                    self.menu_index = clicked
                    return self.activate_main_menu_option()
        return True

    def activate_main_menu_option(self) -> bool:
        self.sound.play("menu", self.volume)
        if self.menu_index == 0:
            self.start_new_game()
        elif self.menu_index == 1:
            self.settings_return_state = GameState.MAIN_MENU
            self.settings_index = 0
            self.state = GameState.SETTINGS
        else:
            return False
        return True

    def handle_settings_event(self, event: pygame.event.Event) -> None:
        row_count = 5
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.settings_index = (self.settings_index - 1) % row_count
                self.sound.play("menu", self.volume)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.settings_index = (self.settings_index + 1) % row_count
                self.sound.play("menu", self.volume)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.change_setting(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.change_setting(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.settings_index == 4:
                    self.state = self.settings_return_state
                else:
                    self.change_setting(1)
            elif event.key == pygame.K_ESCAPE:
                self.state = self.settings_return_state
        elif event.type == pygame.MOUSEMOTION:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                hovered = self.settings_row_at(canvas_pos)
                if hovered is not None:
                    self.settings_index = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if not canvas_pos:
                return
            clicked = self.settings_row_at(canvas_pos)
            if clicked is None:
                return
            self.settings_index = clicked
            if clicked == 4:
                self.state = self.settings_return_state
            else:
                self.change_setting(1)

    def change_setting(self, direction: int) -> None:
        self.sound.play("menu", self.volume)
        if self.settings_index == 0:
            current = DIFFICULTIES.index(self.difficulty)
            self.difficulty = DIFFICULTIES[(current + direction) % len(DIFFICULTIES)]
        elif self.settings_index == 1:
            self.volume = max(0.0, min(1.0, self.volume + 0.1 * direction))
            self.sync_background_music()
        elif self.settings_index == 2:
            self.toggle_fullscreen()
        elif self.settings_index == 3:
            self.horror_mode = not self.horror_mode
            self.update_window_title()
            self.apply_horror_theme()
            self.sync_background_music()

    def handle_playing_event(self, event: pygame.event.Event) -> bool:
        if event.type != pygame.KEYDOWN:
            return False
        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
            return True
        if event.key == pygame.K_r:
            self.restart_level()
        elif event.key == pygame.K_ESCAPE:
            self.pause_index = 0
            self.state = GameState.PAUSED
        return False

    def handle_pause_event(self, event: pygame.event.Event) -> bool:
        options = ("Resume", "Settings", "Main Menu", "Quit")
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.pause_index = (self.pause_index - 1) % len(options)
                self.sound.play("menu", self.volume)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.pause_index = (self.pause_index + 1) % len(options)
                self.sound.play("menu", self.volume)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.activate_pause_option()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
        elif event.type == pygame.MOUSEMOTION:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                hovered = self.menu_option_at(canvas_pos, options, 235)
                if hovered is not None:
                    self.pause_index = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                clicked = self.menu_option_at(canvas_pos, options, 235)
                if clicked is not None:
                    self.pause_index = clicked
                    return self.activate_pause_option()
        return True

    def activate_pause_option(self) -> bool:
        self.sound.play("menu", self.volume)
        if self.pause_index == 0:
            self.state = GameState.PLAYING
        elif self.pause_index == 1:
            self.settings_return_state = GameState.PAUSED
            self.settings_index = 0
            self.state = GameState.SETTINGS
        elif self.pause_index == 2:
            self.menu_index = 0
            self.state = GameState.MAIN_MENU
        else:
            return False
        return True

    def handle_victory_event(self, event: pygame.event.Event) -> bool:
        options = ("Play Again", "Main Menu", "Quit")
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.victory_index = (self.victory_index - 1) % len(options)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.victory_index = (self.victory_index + 1) % len(options)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return self.activate_victory_option()
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MAIN_MENU
        elif event.type == pygame.MOUSEMOTION:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                hovered = self.menu_option_at(canvas_pos, options, 365)
                if hovered is not None:
                    self.victory_index = hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            canvas_pos = self._mouse_to_canvas(event.pos)
            if canvas_pos:
                clicked = self.menu_option_at(canvas_pos, options, 365)
                if clicked is not None:
                    self.victory_index = clicked
                    return self.activate_victory_option()
        return True

    def activate_victory_option(self) -> bool:
        if self.victory_index == 0:
            self.start_new_game()
        elif self.victory_index == 1:
            self.state = GameState.MAIN_MENU
        else:
            return False
        return True

    def handle_collisions(self) -> None:
        collected = pygame.sprite.spritecollide(self.player, self.coins, dokill=True)
        if collected:
            self.score += 10 * len(collected)
            self.sound.play("coin", self.volume)

        if any(self.player.rect.colliderect(spike.hitbox) for spike in self.spikes):
            self.restart_level(penalize=True)
            return

        if self.player.rect.top > SCREEN_HEIGHT + 100:
            self.restart_level(penalize=True)
            return

        for enemy in list(self.enemies):
            if not self.player.rect.colliderect(enemy.hitbox):
                continue

            stomped = (
                self.player.velocity.y > 100
                and self.player.rect.bottom <= enemy.rect.top + 18
            )
            if stomped:
                self.player.bounce(enemy.rect.top)
                enemy_center = enemy.rect.center
                enemy.kill()
                self.score += 40
                self.sound.play("stomp", self.volume)
                if self.horror_mode:
                    self.spawn_blood(enemy_center, 18)
            else:
                self.restart_level(penalize=True)
                return

        goal_active = len(self.coins) == 0
        if goal_active and self.player.rect.colliderect(self.goal.rect):
            self.advance_level()

    def draw(self) -> None:
        if self.state == GameState.MAIN_MENU:
            self.draw_main_menu()
        elif self.state == GameState.SETTINGS:
            self.draw_settings()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        else:
            self.draw_game_world()
            if self.state == GameState.PAUSED:
                self.draw_pause_menu()

    def draw_game_world(self) -> None:
        data = LEVELS[self.level_index]
        if self.horror_mode:
            self.draw_horror_background()
        else:
            self.screen.fill(data.background)
            self.draw_background_details(data.background)
        self.platforms.draw(self.screen)
        self.spikes.draw(self.screen)
        self.coins.draw(self.screen)
        self.enemies.draw(self.screen)
        self.goal.draw(self.screen, active=len(self.coins) == 0)
        if self.death_timer <= 0:
            self.screen.blit(self.player.image, self.player.rect)
        for particle in self.blood_particles:
            particle.draw(self.screen)
        if self.horror_mode:
            self.draw_horror_overlay()
        if self.death_timer > 0:
            death_text = self.title_font.render("YOU DIED", True, COLOR_BRIGHT_BLOOD)
            self.screen.blit(death_text, death_text.get_rect(center=(SCREEN_WIDTH // 2, 210)))
        self.draw_hud(data)

    def draw_main_menu(self) -> None:
        self.draw_menu_background()
        title_text = "BLOOD PLATFORMER" if self.horror_mode else "PIXEL PLATFORMER"
        title_color = COLOR_BRIGHT_BLOOD if self.horror_mode else COLOR_GOLD
        title = self.title_font.render(title_text, True, title_color)
        subtitle = self.small_font.render(
            (
                "Collect cursed souls and survive the blood-soaked levels"
                if self.horror_mode
                else "Collect coins, stomp enemies, reach the flag"
            ),
            True,
            COLOR_WHITE,
        )
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 145)))
        self.screen.blit(subtitle, subtitle.get_rect(center=(SCREEN_WIDTH // 2, 197)))

        options = ("Play", "Settings", "Quit")
        self.draw_menu_options(options, self.menu_index, 300)

        footer = self.small_font.render(
            "Arrow keys / W S + Enter   |   F11 or Alt+Enter: Fullscreen",
            True,
            (195, 202, 215),
        )
        self.screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, 555)))

    def draw_settings(self) -> None:
        self.draw_menu_background()
        title_color = COLOR_BRIGHT_BLOOD if self.horror_mode else COLOR_GOLD
        title = self.title_font.render("SETTINGS", True, title_color)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 88)))

        volume_label = "Muted" if self.volume <= 0.01 else f"{round(self.volume * 100):d}%"
        rows = (
            ("Difficulty", self.difficulty),
            ("Sound volume", volume_label),
            ("Fullscreen", "On" if self.fullscreen else "Off"),
            ("Horror mode", "On" if self.horror_mode else "Off"),
            ("Back", ""),
        )

        start_y = 150
        for index, (label, value) in enumerate(rows):
            selected = index == self.settings_index
            rect = pygame.Rect(230, start_y + index * 68, 500, 52)
            self.draw_panel(rect, selected)
            label_surface = self.menu_font.render(label, True, COLOR_WHITE)
            self.screen.blit(label_surface, (rect.x + 24, rect.centery - label_surface.get_height() // 2))
            if value:
                value_surface = self.menu_font.render(value, True, COLOR_GOLD if selected else COLOR_WHITE)
                self.screen.blit(
                    value_surface,
                    (rect.right - value_surface.get_width() - 24, rect.centery - value_surface.get_height() // 2),
                )

        hint = self.small_font.render(
            "Use Left/Right to change values. Esc returns.", True, (205, 211, 224)
        )
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 535)))

    def draw_pause_menu(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 16, 26, 190))
        self.screen.blit(overlay, (0, 0))

        title = self.title_font.render("PAUSED", True, COLOR_GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 145)))
        self.draw_menu_options(
            ("Resume", "Settings", "Main Menu", "Quit"),
            self.pause_index,
            235,
        )

    def draw_victory(self) -> None:
        self.draw_menu_background()
        title = self.title_font.render(
            "YOU SURVIVED!" if self.horror_mode else f"YOU BEAT ALL {len(LEVELS)} LEVELS!",
            True,
            COLOR_BRIGHT_BLOOD if self.horror_mode else COLOR_GOLD,
        )
        score = self.font.render(f"Final score: {self.score}", True, COLOR_WHITE)
        deaths = self.font.render(f"Deaths: {self.deaths}", True, COLOR_WHITE)
        difficulty = self.small_font.render(
            f"Difficulty: {self.difficulty}", True, (205, 211, 224)
        )

        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 145)))
        self.screen.blit(score, score.get_rect(center=(SCREEN_WIDTH // 2, 225)))
        self.screen.blit(deaths, deaths.get_rect(center=(SCREEN_WIDTH // 2, 265)))
        self.screen.blit(difficulty, difficulty.get_rect(center=(SCREEN_WIDTH // 2, 300)))
        self.draw_menu_options(
            ("Play Again", "Main Menu", "Quit"),
            self.victory_index,
            365,
        )

    def draw_menu_background(self) -> None:
        if self.horror_mode:
            self.screen.fill((20, 2, 7))
            pygame.draw.circle(self.screen, (105, 0, 15), (790, 105), 78)
            pygame.draw.circle(self.screen, (42, 0, 8), (790, 105), 64)
            for x in range(0, SCREEN_WIDTH, 56):
                height = 24 + (x * 17) % 90
                pygame.draw.rect(self.screen, COLOR_DARK_BLOOD, (x, 0, 7, height))
                pygame.draw.circle(self.screen, COLOR_BLOOD, (x + 3, height), 4)
            for _x, _y, radius in ((110, 470, 90), (840, 490, 120)):
                pygame.draw.circle(self.screen, (45, 0, 8), (_x, _y), radius)
        else:
            self.screen.fill((31, 38, 57))
            for x, y, size in ((90, 90, 110), (810, 115, 135), (155, 520, 180), (775, 500, 150)):
                pygame.draw.circle(self.screen, (42, 54, 82), (x, y), size)
            for x in range(0, SCREEN_WIDTH, 64):
                pygame.draw.line(self.screen, (37, 46, 68), (x, 0), (x, SCREEN_HEIGHT), 1)
            for y in range(0, SCREEN_HEIGHT, 64):
                pygame.draw.line(self.screen, (37, 46, 68), (0, y), (SCREEN_WIDTH, y), 1)

        hero = pygame.transform.scale(self.player.image_right, (56, 68))
        enemy = pygame.transform.scale(Enemy._build_image(self.horror_mode), (60, 56))
        self.screen.blit(hero, (130, 245))
        self.screen.blit(enemy, (770, 250))

        if self.horror_mode:
            self.draw_horror_overlay()

    def draw_menu_options(self, options: tuple[str, ...], selected: int, start_y: int) -> None:
        for index, label in enumerate(options):
            rect = self.menu_option_rect(index, start_y)
            self.draw_panel(rect, index == selected)
            surface = self.menu_font.render(label, True, COLOR_WHITE)
            self.screen.blit(surface, surface.get_rect(center=rect.center))

    def draw_panel(self, rect: pygame.Rect, selected: bool) -> None:
        if self.horror_mode:
            fill = (86, 7, 17) if selected else (43, 5, 12)
            border = COLOR_BRIGHT_BLOOD if selected else (115, 18, 29)
        else:
            fill = (58, 75, 112) if selected else (40, 51, 76)
            border = COLOR_GOLD if selected else (83, 97, 126)
        pygame.draw.rect(self.screen, fill, rect, border_radius=10)
        pygame.draw.rect(self.screen, border, rect, 3 if selected else 1, border_radius=10)

    @staticmethod
    def menu_option_rect(index: int, start_y: int) -> pygame.Rect:
        return pygame.Rect(330, start_y + index * 68, 300, 52)

    def menu_option_at(
        self,
        position: tuple[int, int],
        options: tuple[str, ...],
        start_y: int,
    ) -> int | None:
        for index in range(len(options)):
            if self.menu_option_rect(index, start_y).collidepoint(position):
                return index
        return None

    @staticmethod
    def settings_row_at(position: tuple[int, int]) -> int | None:
        for index in range(5):
            if pygame.Rect(230, 150 + index * 68, 500, 52).collidepoint(position):
                return index
        return None

    def draw_background_details(self, background: tuple[int, int, int]) -> None:
        cloud_color = tuple(min(255, value + 55) for value in background)
        for x, y in ((80, 95), (380, 115), (720, 80)):
            pygame.draw.circle(self.screen, cloud_color, (x, y), 24)
            pygame.draw.circle(self.screen, cloud_color, (x + 26, y - 8), 30)
            pygame.draw.circle(self.screen, cloud_color, (x + 55, y), 22)

    def draw_horror_background(self) -> None:
        self.screen.fill((18, 2, 7))

        pygame.draw.circle(self.screen, (130, 0, 18), (785, 115), 72)
        pygame.draw.circle(self.screen, (62, 0, 11), (805, 96), 18)
        pygame.draw.circle(self.screen, (76, 0, 13), (758, 135), 12)

        for x in range(0, SCREEN_WIDTH, 48):
            building_height = 55 + (x * 13) % 115
            pygame.draw.rect(
                self.screen,
                (28, 3, 10),
                (x, SCREEN_HEIGHT - building_height, 42, building_height),
            )
            for window_y in range(SCREEN_HEIGHT - building_height + 14, SCREEN_HEIGHT - 12, 22):
                if (x + window_y) % 3:
                    pygame.draw.rect(self.screen, (82, 0, 15), (x + 9, window_y, 5, 8))

        tick = pygame.time.get_ticks() // 6
        for index in range(34):
            x = (index * 83 + 29) % SCREEN_WIDTH
            y = (tick + index * 47) % (SCREEN_HEIGHT + 90) - 70
            length = 11 + (index * 5) % 22
            pygame.draw.line(self.screen, (105, 0, 17), (x, y), (x - 3, y + length), 2)

    def draw_horror_overlay(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for inset, alpha in ((0, 82), (18, 54), (38, 30)):
            pygame.draw.rect(
                overlay,
                (115, 0, 15, alpha),
                (inset, inset, SCREEN_WIDTH - inset * 2, SCREEN_HEIGHT - inset * 2),
                width=18,
                border_radius=18,
            )

        for x, y, radius in ((34, 92, 18), (910, 170, 24), (72, 520, 20), (875, 548, 28)):
            pygame.draw.circle(overlay, (150, 0, 18, 105), (x, y), radius)
            pygame.draw.circle(overlay, (210, 5, 25, 75), (x + radius // 3, y - radius // 4), max(3, radius // 4))
        self.screen.blit(overlay, (0, 0))

    def draw_hud(self, data: LevelData) -> None:
        panel = pygame.Surface((SCREEN_WIDTH, 68), pygame.SRCALPHA)
        panel.fill((10, 15, 25, 165))
        self.screen.blit(panel, (0, 0))

        level_text = self.font.render(
            f"Level {self.level_index + 1}/{len(LEVELS)}: {data.name}", True, COLOR_WHITE
        )
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_WHITE)
        coins_text = self.small_font.render(f"Coins: {len(self.coins)}", True, COLOR_GOLD)
        enemies_text = self.small_font.render(f"Enemies: {len(self.enemies)}", True, COLOR_ORANGE)
        deaths_text = self.small_font.render(f"Deaths: {self.deaths}", True, COLOR_WHITE)
        mode_text = self.small_font.render(
            "HORROR" if self.horror_mode else "NORMAL",
            True,
            COLOR_BRIGHT_BLOOD if self.horror_mode else COLOR_WHITE,
        )
        controls_text = self.small_font.render(
            "Move: A/D or arrows   Jump: W/Up/Space   Pause: Esc   Restart: R",
            True,
            COLOR_WHITE,
        )

        self.screen.blit(level_text, (16, 9))
        self.screen.blit(score_text, (640, 11))
        self.screen.blit(coins_text, (640, 38))
        self.screen.blit(enemies_text, (750, 38))
        self.screen.blit(deaths_text, (830, 11))
        self.screen.blit(mode_text, (860, 38))
        self.screen.blit(controls_text, (16, 43))

        if self.coins:
            hint = self.small_font.render(
                "Collect every coin to unlock the flag", True, COLOR_BLACK
            )
            hint_bg = pygame.Surface(
                (hint.get_width() + 18, hint.get_height() + 10), pygame.SRCALPHA
            )
            hint_bg.fill((255, 255, 255, 190))
            hint_bg.blit(hint, (9, 5))
            self.screen.blit(
                hint_bg,
                (SCREEN_WIDTH // 2 - hint_bg.get_width() // 2, 78),
            )


if __name__ == "__main__":
    Game().run()
