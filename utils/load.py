import pandas


def export_to_csv(data, filename):
    try:
        df = pandas.DataFrame(data)
        df.to_csv(filename, index=False)
    except Exception as e:
        raise ValueError(f"Failed to export data to CSV: {e}")