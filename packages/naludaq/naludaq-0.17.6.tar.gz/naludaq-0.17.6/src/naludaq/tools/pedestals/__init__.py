def get_pedestals_controller(
    board,
    num_captures: int = 10,
    num_warmup_events: int = 10,
    channels: "list[int]" = None,
):
    """Gets the appropriate pedestals controller for a board.

    Args:
        board (Board): the board
        num_captures (int): Number of datapoints per sample, used for averaging the values.
        num_warmup_events (int): Number of initial events to discard. Helps the board
            settle and excludes events that may skew the pedestals.
        channels (list[int]): channels to generate pedestals for. Defaults to all channels.

    Returns:
        The pedestals controller

    Raises:
        NotImplementedError if the given board does not support pedestals.
    """
    if not board.is_feature_enabled("pedestals"):
        raise NotImplementedError(
            f'Board "{board.model}" does not have support for pedestals.'
        )
    if board.using_new_backend:
        from ._new import get_pedestals_generator_new

        return get_pedestals_generator_new(
            board, num_captures, num_warmup_events, channels
        )

    if board.model in ["upac32", "upaci", "zdigitizer"]:
        from .upac32_pedestals_controller import UpacPedestalsController

        return UpacPedestalsController(board, num_captures, num_warmup_events, channels)
    elif board.model in ["aardvarcv3", "aardvarcv4", "trbhm", "aodsoc_aods", "aodsoc_asoc"]:
        from .aardvarcv3_pedestals_generator import AAv3PedestalsController

        return AAv3PedestalsController(board, num_captures, num_warmup_events, channels)
    elif board.model in ["udc16"]:
        from .udc16_pedestals_generator import UDC16PedestalsGenerator

        return UDC16PedestalsGenerator(board, num_captures, num_warmup_events, channels)
    elif board.model in ["upac96"]:
        from .upac96_pedestals_generator import Upac96PedestalsGenerator

        return Upac96PedestalsGenerator(
            board, num_captures, num_warmup_events, channels
        )
    elif board.model in ["hdsocv1", "hdsocv1_evalr1", "hdsocv1_evalr2"]:
        from .hdsoc_pedestals_controller import HDSoCPedestalsGenerator

        return HDSoCPedestalsGenerator(board, num_captures, num_warmup_events, channels)
    else:
        from .pedestals_controller import PedestalsController

        return PedestalsController(board, num_captures, num_warmup_events, channels)
