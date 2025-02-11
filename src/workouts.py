"""Workouts to choose from."""

MINS = 60


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

    def to_json(self):
        return {ix: value for ix, value in enumerate(self.intervals)}


easy_30min_slow = (
    Workout("Easy 30min Slow")
    .add_interval(3.2, 10 * MINS)
    .add_interval(5.0, 10 * MINS)
    .add_interval(3.6, 10 * MINS)
    .add_interval(4.2, 10 * MINS)
)

easy_40min_slow = (
    Workout("Easy 40min Slow")
    .add_interval(3.2, 15 * MINS)
    .add_interval(5.0, 20 * MINS)
    .add_interval(3.6, 5 * MINS)
)

walk_run = Workout("Walk Run 1.5/2").add_interval(5.1, 5 * MINS)

for _ in range(6):
    walk_run.add_interval(5.1, 1.5 * MINS).add_interval(5.0, 2 * MINS)

walk_run.add_interval(5.1, 5 * MINS)

register = {
    easy_30min_slow.name: easy_30min_slow,
    easy_40min_slow.name: easy_40min_slow,
    walk_run.name: walk_run,
}
