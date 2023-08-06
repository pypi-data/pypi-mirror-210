def get_pedestals_generator_new(
    board,
    num_captures: int = 10,
    num_warmup_events: int = 10,
    channels: "list[int]" = None,
):
    if board.model in ["upac32", "upaci", "zdigitizer"]:
        raise NotImplementedError("Board is currently unsupported")
    elif board.model in [
        "aardvarcv3",
        "aardvarcv4",
        "trbhm",
        "aodsoc_aods",
        "aodsoc_asoc",
    ]:
        from .aav3 import PedestalsGeneratorAardvarcv3New

        return PedestalsGeneratorAardvarcv3New(
            board, num_captures, num_warmup_events, channels
        )
    elif board.model in ["hdsocv1_evalr2"]:
        from .hdsoc import PedestalsGeneratorHdsocNew

        return PedestalsGeneratorHdsocNew(
            board, num_captures, num_warmup_events, channels
        )
    elif board.model in ["udc16"]:
        raise NotImplementedError("Board is currently unsupported")
    elif board.model in ["upac96"]:
        raise NotImplementedError("Board is currently unsupported")
    else:
        from .default import PedestalsGeneratorNew

        return PedestalsGeneratorNew(board, num_captures, num_warmup_events, channels)
