import inspect
from typing import Callable

from bayes_opt import BayesianOptimization, UtilityFunction

from naludaq.helpers.exceptions import OperationCanceledError


class BayesianOptimizer:
    """
    Wrapper function for the bayes_opt module, for any cost function or bounds, with support for
    progress, run, and cancel calls. Bayesian optimization is used for black-box functions where
    you want to find the maximum output by probing the input parameters, using Bayes Theorem to
    estimate the best next input parameters to try.

    References: https://distill.pub/2020/bayesian-optimization/
    """

    def __init__(self, board, cost_function, bounds, **kwargs):
        """
        Initialize a Bayesian Optimization object, which will try to find the maximum output of a
        cost function by probing within the given bounds. Discrete input space is not supported. If
        you want discrete inputs only, that conversion has to happen within the cost function.

        Args:
            board (Board): Board object with active connection
            cost_function (Callable): Function that returns a single float with inputs x and y
            bounds (dict): Dictionary with bounds of the parameter space.

        bounds example: {'x': [1100, 1500], 'y': [900, 1500]}
        """

        self.board = board
        self._cancel = False
        self._progress: list = []

        self.optimizer = BayesianOptimization(f=cost_function, pbounds=bounds, **kwargs)
        self.iteration_history = self.optimizer.res
        self._cancel_flag = 0
        self.iterations = 50

    def maximize(self, n_iter: int) -> dict:
        """
        Finds the input values that result in the maximum output value when run through the cost
        function.

        Args:
            n_iter (int): Number of iterations to run. (i.e. how many attempts to find max value.)

        Returns:
            dict: Dictionary with the stored input params that resulted in the largest output value.
        """
        utility = UtilityFunction(kind="ucb", kappa=2.5, xi=0.0)

        for i in range(n_iter):
            self._raise_if_canceled()

            next_point_to_probe = self.optimizer.suggest(utility)
            target = self.cost_function(**next_point_to_probe)

            self.optimizer.register(params=next_point_to_probe, target=target)

            self._progress.append((int(100 * i / n_iter), f"Scanning {(i+1)}/{n_iter}"))

        return self.optimizer.max

    def run(self):

        self.maximize(self.iterations)

    def cancel(self):

        self._cancel = True

    def _raise_if_canceled(self):
        """Raise an ``OperationCanceledError`` if the cancel flag is set."""
        if self._cancel:
            raise OperationCanceledError("Pedestals generation was canceled.")

    @property
    def progress(self):
        """Get/Set the progress message queue.

        This is a hook to read the progress if running threads.
        """
        return self._progress

    @progress.setter
    def progress(self, value):
        if not hasattr(value, "append"):
            raise TypeError(
                "Progress updates are stored in an object with an 'append' method"
            )
        self._progress = value

    @property
    def cost_function(self):

        return self._cost_function

    @cost_function.setter
    def cost_function(self, cost_func):
        if not type(Callable):
            raise TypeError("Cost Function has to be a function")
        self._verify_cost_function_or_raise(cost_func)
        self._cost_function = cost_func

    def _verify_cost_function_or_raise(self, cost_function):
        sig = inspect.signature(cost_function)

        try:
            x_param = sig.parameters["x"]
            y_param = sig.parameters["y"]
        except KeyError:
            raise KeyError("Cost function MUST have an x and y parameter")

        if x_param.annotation not in [float, int]:
            raise TypeError(
                "Cost function x parameter must be float or int (must have type signature to verify)"
            )

        if y_param.annotation not in [float, int]:
            raise TypeError(
                "Cost function y parameter must be float or int (must have type signature to verify)"
            )
