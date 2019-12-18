"""
Class for Logfiles
"""
import datetime

import pandas as pd


class Logfile(object):
    """Makes a Pandas Dataframe from a logfile"""

    def __init__(self, log, esm_style=True):
        self.log = log
        if esm_style:
            self.log_df = self._generate_dataframe_from_esm_logfile()
        else:
            self.log_df = self._generate_dataframe_from_mpimet_logfile()
        del self.log

    def _generate_dataframe_from_esm_logfile(self):
        df = pd.DataFrame(
            [l.split(" : ") for l in self.log], columns=["Date", "Message"]
        )
        df2 = df["Message"].str.split(expand=True)
        # We drop the first row since it says "Start of Experiment"
        log_df = pd.concat([df[1:]["Date"], df2[1:]], axis=1)
        log_df.columns = [
            "Date",
            "Run Number",
            "Exp Date",
            "Job ID",
            "Seperator",
            "State",
        ]
        log_df.drop("Seperator", axis=1, inplace=True)
        log_df.set_index("Date", inplace=True)
        log_df.index = pd.to_datetime(log_df.index)
        return log_df

    def _generate_dataframe_from_mpimet_logfile(self):
        log_df = pd.read_table(
            self.log,
            sep=r" :  | -",
            skiprows=1,
            infer_datetime_format=True,
            names=["Date", "Message", "State"],
            engine="python",
            index_col=0,
        )
        middle_column = log_df["Message"].apply(lambda x: pd.Series(str(x).split()))
        log_df.drop("Message", axis=1, inplace=True)
        middle_column.columns = ["Run Number", "Exp Date", "Job ID"]
        log_df = pd.concat([log_df, middle_column], axis=1)
        # FIXME: This needs a context manager to try different locales
        log_df.set_index(pd.to_datetime(log_df.index), inplace=True)
        return log_df

    @classmethod
    def from_file(cls, fin):
        with open(fin) as f:
            log = f.readlines()
        return cls(log)

    def compute_throughput(self):
        starts = self.log_df[self.log_df.State.str.contains("start")]
        ends = self.log_df[self.log_df.State.str.contains("done")]
        # Drop the duplicated starts:
        starts.drop_duplicates(subset="Run Number", keep="last", inplace=True)
        merged = pd.concat([starts, ends])
        groupby = merged.groupby("Run Number")
        run_diffs = {"Run Number": [], "Wall Time": [], "Queue Time": []}
        for name, group in groupby:
            if int(name) > 1:
                previous_group = groupby.get_group(str(int(name) - 1))
                run_diffs["Queue Time"].append(
                    group.index[0] - previous_group.index[-1]
                )
            else:
                run_diffs["Queue Time"].append(datetime.timedelta(0))
            run_diffs["Run Number"].append(int(name))
            run_diffs["Wall Time"].append(group.index[-1] - group.index[0])
        diffs = (
            pd.DataFrame(run_diffs).sort_values("Run Number").set_index("Run Number")
        )
        throughput = (datetime.timedelta(1) / diffs.mean())["Wall Time"]
        return pd.DataFrame({"Simulation Average": diffs.mean()}), throughput, diffs

    def run_stats(self):
        _, _, diffs = self.compute_throughput()
        last_ten_diffs = diffs.tail(10)
        throughput = datetime.timedelta(1) / last_ten_diffs["Wall Time"].mean()
        efficiency = last_ten_diffs["Wall Time"].mean() / (
            last_ten_diffs["Queue Time"].mean() + last_ten_diffs["Wall Time"].mean()
        )

        df = pd.DataFrame.from_dict(
            {
                "Mean Walltime": last_ten_diffs["Wall Time"].mean(),
                "Mean Queuing Time": last_ten_diffs["Queue Time"].mean(),
                "Optimal Throughput": throughput,
                "Actual Throughput (Last 10 Runs)": throughput * efficiency,
                "Run Efficiency (Last 10 Runs)": efficiency * 100,
            },
            orient="index",
            # columns=["Run Statistics"],
        )
        return df
