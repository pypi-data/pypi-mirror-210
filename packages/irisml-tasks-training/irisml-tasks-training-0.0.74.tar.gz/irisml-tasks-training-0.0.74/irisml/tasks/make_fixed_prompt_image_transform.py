import dataclasses
import typing
import PIL.Image
import torch
import irisml.core


class Task(irisml.core.TaskBase):
    """Make a transform function for image and a fixed prompt.

    The interface of the transform function is:
    - Input: PIL.Image.Image
    - Output: Tuple[str, List[torch.Tensor]]

    Config:
        prompt (str): The prompt to use.
    """

    VERSION = '0.1.0'

    @dataclasses.dataclass
    class Inputs:
        image_transform: typing.Callable[[PIL.Image.Image], torch.Tensor]

    @dataclasses.dataclass
    class Config:
        prompt: str

    @dataclasses.dataclass
    class Outputs:
        transform: typing.Callable

    def execute(self, inputs):
        transform = FixedPromptImageTransform(inputs.image_transform, self.config.prompt)
        return self.Outputs(transform=transform)

    def dry_run(self, inputs):
        return self.execute(inputs)


class FixedPromptImageTransform:
    def __init__(self, image_transform, prompt):
        self._image_transform = image_transform
        self._prompt = prompt

    def __call__(self, inputs, targets):
        assert isinstance(inputs, PIL.Image.Image)
        image_tensor = self._image_transform(inputs)
        assert isinstance(image_tensor, torch.Tensor)
        return (self._prompt, [image_tensor]), targets
