import numpy
import pandas

from lmtanalysis import Measure

class DetectionFeatures():
    @staticmethod
    def total_distance(df, region=None):
        name = "Distance"
        magic_thres = 85.5
        dists = numpy.sqrt(numpy.square(df[["x", "y"]].diff()).sum(1))

        if region is None:
            value = dists[dists <= magic_thres].sum()
        else:
            value = dists[df[region] & (dists <= magic_thres)].sum()
            name += f"_{region}"

        return pandas.Series({name: value * Measure.scaleFactor})

    @staticmethod
    def total_time(df, region=None):
        name = "Time_spent"
        dists = numpy.sqrt(numpy.square(df[["sec"]].diff()).sum(1))

        if region is None:
            value = dists.sum()
        else:
            value = dists[df[region]].sum()
            name += f"_{region}"

        return pandas.Series({name: value })

    @staticmethod
    def speed_avg(df, region=None):
        name = "Speed_average"
        if region is not None:
            name += f"_{region}"
        return pandas.Series({name: DetectionFeatures.total_distance(df, region).values[0] /
                                        DetectionFeatures.total_time(df, region).values[0]})

class EventFeatures():
    @staticmethod
    def duration_stats(df):
        return pandas.Series({
                            "Duration_mean":   df["duration"].mean(),
                            "Duration_median": df["duration"].median(),
                            "Duration_std":    df["duration"].std(),
                            })


def computeDetectionFeatures(animal_pool, start="0min", end="60min", freq="5min"):
    """Computes common features of the mouse trajectories in the animal pool,
       for a given time interval range given by start, end and freq (temporal bin size).

       Use pandas convention to specifiy time parameters.
           * 3 hours  : "3H"
           * 5 minutes: "5min"

        Features computed:
            * time spent
            * distance travelled
            * average speed


    Args:
        animal_pool (AnimalPool): the animal pool
        start (str, optional): Start time. Defaults to "0min".
        end (str, optional)  : End time.   Defaults to "60min".
        freq (str, optional) : Time step.  Defaults to "5min".

    Returns:
        DataFrame: Multiindex Dataframe containing mouse meta information and
                   computed features:

    """
    detection_table = animal_pool.getDetectionTable()
    time_delta_rng = pandas.timedelta_range(start=start, end=end, freq=freq)

    grp = detection_table.groupby(["RFID", pandas.cut(detection_table.time, bins=time_delta_rng)])
    return pandas.concat([
                        grp.name.first(),
                        grp.genotype.first(),
                        grp.apply(DetectionFeatures.total_time),
                        grp.apply(DetectionFeatures.total_time, "in_arena_center"),

                        grp.apply(DetectionFeatures.total_distance),
                        grp.apply(DetectionFeatures.total_distance, "in_arena_center"),

                        grp.apply(DetectionFeatures.speed_avg),
                        grp.apply(DetectionFeatures.speed_avg, "in_arena_center")
                    ], axis=1)

def computeEventFeatures(animal_pool, start="0min", end="60min", freq="5min"):
    """Computes common features of the mice' events in the animal pool,
       for a given time interval range given by start, end and freq (temporal bin size).

       Use pandas convention to specifiy time parameters.
           * 3 hours  : "3H"
           * 5 minutes: "5min"

        Features computed:
            * number of events
            * duration of events
                * mean/median/std


    Args:
        animal_pool (AnimalPool): the animal pool
        start (str, optional): Start time. Defaults to "0min".
        end (str, optional)  : End time.   Defaults to "60min".
        freq (str, optional) : Time step.  Defaults to "5min".

    Returns:
        DataFrame: Multiindex Dataframe containing mouse meta information and
                   computed event features:

    """
    events_table = animal_pool.getAllEventsTable()
    time_delta_rng = pandas.timedelta_range(start=start, end=end, freq=freq)

    grp = events_table.groupby(["event_name", "RFID",  pandas.cut(events_table.time, bins=time_delta_rng)])
    res = pandas.concat([
                   grp.name.first(),
                   grp.genotype.first(),
                   grp.size(),
                   grp.apply(EventFeatures.duration_stats)
    ], axis=1)
    res = res.rename(columns={0: "Number_of_events"})
    return res