from __future__ import annotations

import sys
from pathlib import Path

import autopep8  # pyright: ignore[reportMissingTypeStubs]
import click
import yaml
from result import Err, Ok

from connexion_code_generator.generator import Generator
from connexion_code_generator.generator.entities import SecurityRequirementInfo
from connexion_code_generator.parser import OpenAPI30


@click.command()
@click.option("-i", "--input", "input_", default="./openapi.yaml")
@click.option("-d", "--dto-module-path", "dto_module_path", default="api.dtos")
@click.option("-o", "--output", "output_", default="./api/views.py")
@click.option("-e", "--error-type", "error_response_type", default="ErrorResponse")
@click.option("--abstract", is_flag=True, default=False, help="Generate abstract class instead of protocol class.")
@click.option("--sync", is_flag=True, default=False, help="Generate sync methods instead of async methods.")
def generate(input_: str, dto_module_path: str, output_: str, error_response_type: str, *, abstract: bool, sync: bool) -> None:  # noqa: E501
    with Path(input_).open() as f:
        spec_dict = yaml.load(f, Loader=yaml.SafeLoader)

    spec = OpenAPI30.parse_obj(spec_dict)
    security_requirements_map = {
        ("jwt",): SecurityRequirementInfo(parameter_name="user", parameter_data_type="UUID"),
        ("visitor",): SecurityRequirementInfo(parameter_name="user", parameter_data_type="UUID"),
        ("jwt", "visitor"): SecurityRequirementInfo("token_info", "TokenInfo"),
    }

    generator = Generator(
        spec,
        security_requirements_map,
        dto_module_path,
        error_response_type,
        "protocol" if abstract is False else "abstract",
        "async" if sync is False else "sync",
    )

    match generator.generate():
        case Err(e):
            click.echo(e)
            return
        case Ok(res):
            pass

    output_path = Path(output_)
    output_path_parent = output_path.parent
    output_path_parent.mkdir(parents=True, exist_ok=True)
    (output_path_parent / "__init__.py").touch()

    with output_path.open("w") as f:
        _ = f.write(res)

    sys.exit(autopep8.main(argv=["autopep8", "--in-place", output_]))  # pyright: ignore[reportUnknownArgumentType]
