import pandas as pd


def modify_dataframe_at(main_df: pd.DataFrame, indx: int, dict_updater: dict):
    for col_key, new_val in dict_updater.items():
        main_df.at[indx, col_key] = new_val


def sort_dataframe(main_df: pd.DataFrame, order_list: list, sorting_key: str) -> pd.DataFrame:
    """Sorts a DataFrame based on a specified order list and a sorting key."""

    def custom_sort(value):
        if value in order_list:
            return order_list.index(value), value
        else:
            # Custom alphabetical sorting
            return len(order_list), value

    # Apply the custom sorting function to the sorting_key column
    main_df['sorting_key'] = main_df[sorting_key].apply(custom_sort)

    # Sort the DataFrame based on the sorting_key
    sorted_df = main_df.sort_values(by='sorting_key').drop(columns='sorting_key')

    return sorted_df
