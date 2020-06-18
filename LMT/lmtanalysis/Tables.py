import numpy
import pandas

from lmtanalysis import Measure

class DetectionTableAnalysis():
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
        return pandas.Series({name: DetectionTableAnalysis.total_distance(df, region).values[0] /
                                        DetectionTableAnalysis.total_time(df, region).values[0]})

class EventTableAnalysis():
    @staticmethod
    def duration_stats(df):
        return pandas.Series({
                            "Duration_mean":   df["duration"].mean(),
                            "Duration_median": df["duration"].median(),
                            "Duration_std":    df["duration"].std(),
                            })


def getDetectionSummary(animal_pool, start="0min", end="60min", freq="5min"):
    detection_table = animal_pool.getDetectionTable()
    time_delta_rng = pandas.timedelta_range(start=start, end=end, freq=freq)

    grp = detection_table.groupby(["RFID", pandas.cut(detection_table.time, bins=time_delta_rng)])
    return pandas.concat([
                        grp.name.first(),
                        grp.genotype.first(),
                        grp.apply(DetectionTableAnalysis.total_time),
                        grp.apply(DetectionTableAnalysis.total_time, "in_arena_center"),

                        grp.apply(DetectionTableAnalysis.total_distance),
                        grp.apply(DetectionTableAnalysis.total_distance, "in_arena_center"),

                        grp.apply(DetectionTableAnalysis.speed_avg),
                        grp.apply(DetectionTableAnalysis.speed_avg, "in_arena_center")
                    ], axis=1)

def getEventSummary(animal_pool, start="0min", end="60min", freq="5min"):
    events_table = animal_pool.getAllEventsTable()
    time_delta_rng = pandas.timedelta_range(start=start, end=end, freq=freq)

    grp = events_table.groupby(["event_name", "RFID",  pandas.cut(events_table.time, bins=time_delta_rng)])
    res = pandas.concat([
                   grp.name.first(),
                   grp.genotype.first(),
                   grp.size(),
                   grp.apply(EventTableAnalysis.duration_stats)
    ], axis=1)
    res = res.rename(columns={0: "Number_of_events"})
    return res