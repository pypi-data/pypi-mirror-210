"""Helper functions for validating inputs."""
import pathlib


def validate_dir_or_raise(output_dir, name="Directory"):
    if not isinstance(output_dir, (str, pathlib.Path)):
        raise TypeError(f"{name} must be a string.")
    if not pathlib.Path(output_dir).exists():
        raise FileNotFoundError(f"{name} must exist.")
    if output_dir is None or not pathlib.Path(output_dir).is_dir():
        raise NotADirectoryError(f"{name} must be specified.")
