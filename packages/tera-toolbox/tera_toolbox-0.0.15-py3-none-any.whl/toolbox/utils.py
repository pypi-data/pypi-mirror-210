import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# from . import data


def extract_values_from_key(list_of_dicts, key):
    return [d[key] for d in list_of_dicts if key in d]


def count_days(start_date, end_date, business=True, calendar="anbima", holidays=[]):
    date_range = pd.date_range(start_date, end_date, freq="D")

    if business:
        # if calendar is not None:
        #     calendar_holidays = data.holidays(calendar)
        #     calendar_holidays = extract_values_from_key(calendar_holidays, "data")
        #     holidays.extend(calendar_holidays)

        holidays = pd.to_datetime(holidays)
        weekdays = np.isin(date_range.weekday, [5, 6], invert=True)
        non_holidays = np.isin(date_range, holidays, invert=True)
        valid_days = np.logical_and(weekdays, non_holidays).sum()
    else:
        valid_days = len(date_range)

    return valid_days - 1


def add_days(
    start_date,
    num_days=0,
    num_months=0,
    num_years=0,
    business=True,
    calendar="anbima",
    holidays=[],
):
    date_format = "%Y-%m-%d"
    start_date = datetime.strptime(start_date, date_format)

    # if calendar is not None:
    #     calendar_holidays = data.holidays(calendar)
    #     calendar_holidays = extract_values_from_key(calendar_holidays, "data")
    #     holidays.extend(calendar_holidays)

    holidays = [datetime.strptime(h, date_format) for h in holidays]

    new_date = start_date + relativedelta(
        days=num_days, months=num_months, years=num_years
    )

    if business:
        while new_date.weekday() in (5, 6) or new_date in holidays:
            new_date += timedelta(days=1)

    return new_date.strftime(date_format)


def random_bool(p, N):
    return np.random.choice(a=[True, False], size=(N,), p=[p, 1 - p])


def evolucao_patrimonio(
    pl_inicial,
    ap,
    ex,
    months=1200,
    freq_ap=1,
    timing_ap=False,
    max_ap=999999999,
    max_ex=999999999,
    ap_till=720,
    ap_from=1,
    freq_ex=1,
    timing_ex=True,
    ex_till=1200,
    ex_from=1,
    juro_real=0.02,
    step_freq_ap=0,
    step_ap=0.0,
    step_freq_ex=0,
    step_ex=0.0,
    extra_ap=0,
    extra_prob_ap=0.0,
    extra_ex=0,
    extra_prob_ex=0.0,
    extra=[],
):
    extra = pd.DataFrame(np.array(extra), columns=["months", "aportes", "despesas"])
    df = pd.DataFrame(np.arange(1, months + 1, 1), columns=["months"])
    df["years"] = df["months"] / 12
    df["aportes"] = np.minimum(
        max_ap,
        (
            (df["months"] % freq_ap == 0)
            & (df["months"] <= ap_till)
            & (df["months"] >= ap_from)
        )
        * (ap * (1 + step_ap) ** (df["months"] // step_freq_ap)),
    ) + extra_ap * random_bool(extra_prob_ap, months)
    df["despesas"] = np.minimum(
        max_ex,
        (
            (df["months"] % freq_ex == 0)
            & (df["months"] <= ex_till)
            & (df["months"] >= ex_from)
        )
        * (ex * (1 + step_ex) ** (df["months"] // step_freq_ex)),
    ) + extra_ex * random_bool(extra_prob_ex, months)

    df["aportes"] = df["aportes"] + extra["aportes"]
    df["despesas"] = df["despesas"] + extra["despesas"]

    return calculate(df, pl_inicial, timing_ap, timing_ex, juro_real)


def calculate(df, pl_inicial, timing_ap, timing_ex, juro_real):
    juro_real = (1 + juro_real) ** (1 / 12) - 1
    result = []
    for i, r in df.iterrows():
        result.append(
            (
                (pl_inicial if i == 0 else result[i - 1])
                + (r["aportes"] if timing_ap else 0)
                - (r["despesas"] if timing_ex else 0)
            )
            * (1 + juro_real)
            + (r["aportes"] if not timing_ap else 0)
            - (r["despesas"] if not timing_ex else 0)
        )
    df["patrimonio"] = result

    return df
