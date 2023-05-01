"""A simple profiler with LineProfiler."""

from line_profiler import LineProfiler

profiler = LineProfiler()


def profile(func):
    """Simple profiler with LineProfiler."""

    def inner(*args, **kwargs):
        profiler.add_function(func)
        profiler.enable_by_count()
        return func(*args, **kwargs)

    return inner


def profile_print_stats():
    """Print stat for the annotated @profile"""
    profiler.print_stats()
