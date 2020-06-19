"""
.. module:: utils.

   :synopsis: Utility functions used throughout the application.
"""



roles = [("User", "User"), ("Administrator", "Administrator")]



class InvalidResetToken(Exception):
    pass


def eval_request_bool(val, default=False):
    """
    Evaluates the boolean value of a request parameter.
    :param val: the value to check
    :param default: bool to return by default
    :return: Boolean
    """
    assert isinstance(default, bool)
    if val is not None:
        val = val.lower()
        if val in ["False", "false", "0", "n", "no", "off"]:
            return False
        if val in ["True", "true", "1", "y", "yes", "on"]:
            return True
    return default
