import copy
import dataclasses
import torch.nn
import irisml.core


class Task(irisml.core.TaskBase):
    """Split a image-text model into an image model and a text model.

    Inputs:
        model (torch.nn.Module): An input model. It must have 'image_model' and 'text_model' attributes.

    Config:
        append_normalizer (bool): If True, append a normalization module to the end of the image and text models.
    """
    VERSION = '0.1.2'

    @dataclasses.dataclass
    class Inputs:
        model: torch.nn.Module

    @dataclasses.dataclass
    class Config:
        append_normalizer: bool = True

    @dataclasses.dataclass
    class Outputs:
        image_model: torch.nn.Module
        text_model: torch.nn.Module
        logit_scale: torch.Tensor

    def execute(self, inputs):
        image_modules = [copy.deepcopy(inputs.model.image_model), copy.deepcopy(inputs.model.image_projection)]
        text_modules = [copy.deepcopy(inputs.model.text_model), copy.deepcopy(inputs.model.text_projection)]

        if self.config.append_normalizer:
            image_modules.append(NormModule())
            text_modules.append(NormModule())

        image_model = torch.nn.Sequential(*image_modules)
        text_model = torch.nn.Sequential(*text_modules)
        logit_scale = copy.deepcopy(inputs.model.logit_scale)
        return self.Outputs(image_model, text_model, logit_scale)

    def dry_run(self, inputs):
        return self.execute(inputs)


class NormModule(torch.nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        x = x / x.norm(dim=-1, keepdim=True)
        return x
