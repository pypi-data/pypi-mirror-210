
def sort_by_key(info_list, sort_key, reverse=False):
    def get_value(info):
        return info.get(sort_key)
    info_list.sort(key=get_value, reverse=reverse)


# deduplicate rows
# change rows from
#   key1 key1-1 key1-1-1 value1
#   key1 key1-1 key1-1-2 value2
#   key1 key1-2 key1-2-1 value3
#   key1 key1-2 key1-2-2 value4
# to:
#   key1 key1-1 key1-1-1 value1
#               key1-1-2 value2
#        key1-2 key1-2-1 value1
#               key1-2-2 value2
def dedup_rows(rows, dedup_indexs):
    if len(rows) == 0:
        return rows
    rst = list()
    last_row = [''] * len(rows[0])
    for row in rows:
        deduped_row = list(row)
        for index, column_value in enumerate(row):
            if index in dedup_indexs and row[index] == last_row[index]:
                deduped_row[index] = ''
        rst.append(deduped_row)
        last_row = row
    return rst

