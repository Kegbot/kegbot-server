"""Methods for manipulating a time series.

A Kegbot core may report a time series (Drink.tick_time_series) for the meter
events that caused a drink.
"""


def from_string(s):
    """Converts a time series to a list of (int, int) tuples.

    The string should be a sequence of zero or more <time>:<amount> pairs.
    Whitespace delimits each pair; leading and trailing whitespace is ignored.

    ValueError is raised on any malformed input.
    """
    pairs = s.strip().split()
    ret = []
    for pair in pairs:
        time, amount = pair.split(":")
        time = int(time)
        amount = int(amount)
        if time < 0:
            raise ValueError("Time cannot be less than zero: %s" % time)
        ret.append((time, amount))
    return ret


def to_string(pairs):
    """Converts a series of (int, int) tuples to a time series string."""
    return " ".join("%i:%i" % pair for pair in pairs)
