import base64
import io
from enum import StrEnum
from typing import Annotated, List, Optional

from pydantic import (
    AnyUrl,
    BaseModel,
    EmailStr,
    confloat,
    conint,
    constr,
    validator,
)

class Type(StrEnum):
    AUDIO = "AUDIO"
    CLASSIFICATION = "CLASSIFICATION"
    PICTURE = "PICTURE"
    STORAGE = "STORAGE"
    TEXT = "TEXT"
    VIDEO = "VIDEO"


class Engine(BaseModel):
    description: str
    id: str
    name: str
    type: Type


class Error(BaseModel):
    id: str
    name: str
    message: str


CfgScale = Annotated[float, confloat(ge=0.0, le=35.0)]


class ClipGuidancePreset(StrEnum):
    FAST_BLUE = "FAST_BLUE"
    FAST_GREEN = "FAST_GREEN"
    NONE = "NONE"
    SIMPLE = "SIMPLE"
    SLOW = "SLOW"
    SLOWER = "SLOWER"
    SLOWEST = "SLOWEST"


UpscaleImageHeight = Annotated[int, conint(ge=512)]

UpscaleImageWidth = Annotated[int, conint(ge=512)]

DiffuseImageHeight = Annotated[int, conint(ge=128, multiple_of=64)]

DiffuseImageWidth = Annotated[int, conint(ge=128, multiple_of=64)]


class Sampler(StrEnum):
    DDIM = "DDIM"
    DDPM = "DDPM"
    K_DPMPP_2M = "K_DPMPP_2M"
    K_DPMPP_2S_ANCESTRAL = "K_DPMPP_2S_ANCESTRAL"
    K_DPM_2 = "K_DPM_2"
    K_DPM_2_ANCESTRAL = "K_DPM_2_ANCESTRAL"
    K_EULER = "K_EULER"
    K_EULER_ANCESTRAL = "K_EULER_ANCESTRAL"
    K_HEUN = "K_HEUN"
    K_LMS = "K_LMS"


Samples = Annotated[int, conint(ge=1, le=10)]

Seed = Annotated[int, conint(ge=0, le=4294967295)]

Steps = Annotated[int, conint(ge=10, le=150)]

Extras = dict


class StylePreset(StrEnum):
    enhance = "enhance"
    anime = "anime"
    photographic = "photographic"
    digital_art = "digital-art"
    comic_book = "comic-book"
    fantasy_art = "fantasy-art"
    line_art = "line-art"
    analog_film = "analog-film"
    neon_punk = "neon-punk"
    isometric = "isometric"
    low_poly = "low-poly"
    origami = "origami"
    modeling_compound = "modeling-compound"
    cinematic = "cinematic"
    field_3d_model = "3d-model"
    pixel_art = "pixel-art"
    tile_texture = "tile-texture"


class TextPrompt(BaseModel):
    text: Annotated[str, constr(max_length=2000)]
    weight: Optional[float] = None

SingleTextPrompt = str

TextPrompts = List[TextPrompt]

InitImage = bytes

InitImageStrength = Annotated[float, confloat(ge=0.0, le=1.0)]


class InitImageMode(StrEnum):
    IMAGE_STRENGTH = "IMAGE_STRENGTH"
    STEP_SCHEDULE = "STEP_SCHEDULE"


StepScheduleStart = Annotated[float, confloat(ge=0.0, le=1.0)]

StepScheduleEnd = Annotated[float, confloat(ge=0.0, le=1.0)]

MaskImage = bytes

MaskSource = str


class GenerationRequestOptionalParams(BaseModel):
    cfg_scale: Optional[CfgScale] = None
    clip_guidance_preset: Optional[ClipGuidancePreset] = None
    sampler: Optional[Sampler] = None
    samples: Optional[Samples] = None
    seed: Optional[Seed] = None
    steps: Optional[Steps] = None
    style_preset: Optional[StylePreset] = None
    extras: Optional[Extras] = None


class LatentUpscalerUpscaleRequestBody(BaseModel):
    image: InitImage
    width: Optional[UpscaleImageWidth] = None
    height: Optional[UpscaleImageHeight] = None
    text_prompts: Optional[TextPrompts] = None
    seed: Optional[Seed] = None
    steps: Optional[Steps] = None
    cfg_scale: Optional[CfgScale] = None


class ImageToImageRequestBody(BaseModel):
    text_prompts: TextPrompts
    init_image: InitImage
    init_image_mode: Optional[InitImageMode] = InitImageMode("IMAGE_STRENGTH")
    image_strength: Optional[InitImageStrength] = None
    step_schedule_start: Optional[StepScheduleStart] = None
    step_schedule_end: Optional[StepScheduleEnd] = None
    cfg_scale: Optional[CfgScale] = None
    clip_guidance_preset: Optional[ClipGuidancePreset] = None
    sampler: Optional[Sampler] = None
    samples: Optional[Samples] = None
    seed: Optional[Seed] = None
    steps: Optional[Steps] = None
    style_preset: Optional[StylePreset] = None
    extras: Optional[Extras] = None


class MaskingRequestBody(BaseModel):
    init_image: InitImage
    mask_source: MaskSource
    mask_image: Optional[MaskImage] = None
    text_prompts: TextPrompts
    cfg_scale: Optional[CfgScale] = None
    clip_guidance_preset: Optional[ClipGuidancePreset] = None
    sampler: Optional[Sampler] = None
    samples: Optional[Samples] = None
    seed: Optional[Seed] = None
    steps: Optional[Steps] = None
    style_preset: Optional[StylePreset] = None
    extras: Optional[Extras] = None


class TextToImageRequestBody(GenerationRequestOptionalParams):
    height: Optional[DiffuseImageHeight] = None
    width: Optional[DiffuseImageWidth] = None
    text_prompts: TextPrompts


class ImageToImageUpscaleRequestBody(BaseModel):
    image: InitImage
    width: Optional[UpscaleImageWidth]
    height: Optional[UpscaleImageHeight]

    @validator("width", always=True)
    def mutually_exclusive(cls, v, values):
        if values["height"] is not None and v:
            raise ValueError("You can only specify one of width and height.")
        return v


class BalanceResponseBody(BaseModel):
    credits: float


ListEnginesResponseBody = List[Engine]


class FinishReason(StrEnum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CONTENT_FILTERED = "CONTENT_FILTERED"


class Image(BaseModel):
    base64: Optional[str] = None
    finishReason: Optional[FinishReason] = None
    seed: Optional[float] = None

    @property
    def file(self):
        assert self.base64 is not None
        return io.BytesIO(base64.b64decode(self.base64))


class OrganizationMembership(BaseModel):
    id: str
    is_default: bool
    name: str
    role: str


class AccountResponseBody(BaseModel):
    email: EmailStr
    id: str
    organizations: List[OrganizationMembership]
    profile_picture: Optional[AnyUrl] = None


class TextToImageResponseBody(BaseModel):
    artifacts: List[Image]


class ImageToImageResponseBody(BaseModel):
    artifacts: List[Image]


class ImageToImageUpscaleResponseBody(BaseModel):
    artifacts: List[Image]
