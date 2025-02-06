"""Workouts to choose from."""

SEC_TO_MIN = 60


class Workout:
    """Store a workout.

    Comprises of multiple intervals,
     each interval is a speed setting for a certain duration
    """

    def __init__(self, name: str):
        """Initialise the workout."""
        self.name = name
        self.intervals: list[tuple[float, int]] = []

    def add_interval(self, speed_ms: float, duration_s: int):
        """Add and interval.

        Returns 'self' to allow chaining of method calls.
        """
        self.intervals.append((speed_ms, duration_s))
        return self


easy_30min_slow = (
    Workout("Easy 30min Slow")
    .add_interval(3.2, 10 * SEC_TO_MIN)
    .add_interval(5.0, 15 * SEC_TO_MIN)
    .add_interval(3.6, 10 * SEC_TO_MIN)
)
