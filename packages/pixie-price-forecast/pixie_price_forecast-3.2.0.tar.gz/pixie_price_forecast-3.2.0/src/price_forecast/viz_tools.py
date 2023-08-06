import matplotlib.pyplot as plt


def compare_cleansing(df_ref, df_filtered, province_name, reference_column):
    df_ref[reference_column].plot(label='before filtering', alpha=0.5)
    df_filtered[reference_column].plot(label='after filtering', alpha=0.5)
    plt.title(f'Filtering for {province_name}')
    plt.xticks(rotation=90)
    plt.ylabel('# Ads')
    plt.legend()
    plt.grid()
    plt.show()
