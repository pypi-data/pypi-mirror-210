# Stability AI

An **UNOFFICIAL** client library for the stability.ai REST API.

## Motivation

The official `stability-sdk` is a based on gRPC and also really hard to use. Like look at this, this
ignores setting up the SDK.

```python
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation

answers = stability_api.generate(
    prompt="a rocket-ship launching from rolling greens with blue daisies",
    seed=892226758,
    steps=30,
    cfg_scale=8.0,
    width=512,
    height=512,
    sampler=generation.SAMPLER_K_DPMPP_2M
)

for resp in answers:
    for artifact in resp.artifacts:
        if artifact.finish_reason == generation.FILTER:
            warnings.warn(
                "Your request activated the API's safety filters and could not be processed."
                "Please modify the prompt and try again.")
        if artifact.type == generation.ARTIFACT_IMAGE:
            global img
            img = Image.open(io.BytesIO(artifact.binary))
            img.save(str(artifact.seed)+ ".png")
```

This for loop is *magic*. You must loop the results in exactly this way or the gRPC library won't
work. It's about an unpythonic as a library can get.

## My Take

```python
# Set the STABILITY_API_KEY environment variable.

from stabilityai.client import AsyncStabilityClient
from stabilityai.models import Sampler

async def example():
  async with AsyncStabilityClient() as stability:
    results = await stability.text_to_image(
        text_prompt="a rocket-ship launching from rolling greens with blue daisies",
        # All these are optional and have sane defaults.
        seed=892226758,
        steps=30,
        cfg_scale=8.0,
        width=512,
        height=512,
        sampler=Sampler.K_DPMPP_2M,
    )

    artifact = results.artifacts[0]

    img = Image.open(artifact.file)
    img.save(artifact.file.name)
```

## Additional Nicetieis

* Instead of manually checking `FINISH_REASON` an appropriate exception will automatically be
    raised.

* Full mypy/pyright support for type checking and autocomplete.
