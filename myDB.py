import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

def get_categories(level: int, old_path: str = '') -> list:
    result = []
    all_paths = cursor.execute("SELECT path FROM formuls").fetchall()
    old_categories = old_path.split('/')
    for path in all_paths:
        categories = path[0].split('/')
        if old_path != '':
            for old_cat in old_categories:
                if old_cat in categories:
                    if categories[level] not in result:
                        result.append(categories[level])
        else:
            if categories[level] not in result:
                result.append(categories[level])
    return result


def get_col_levels():
    


if __name__ == '__main__':
    print(get_categories(0))
