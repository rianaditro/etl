import pandas


def export_to_csv(data, filename):
    df = pandas.DataFrame(data)
    df.to_csv(filename, index=False)