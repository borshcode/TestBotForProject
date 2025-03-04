import sqlite3

from downloadPhoto import get_name

db = sqlite3.connect('database.db')
cursor = db.cursor()

def get_categories(level: int, old_path: str = ''):
    '''
    Если все нормально, возвращает категории.
    Если каталогов нет, то возвращает 1
    '''
    result = []
    all_paths = cursor.execute("SELECT path FROM formuls").fetchall()
    old_categories = old_path.split('/')
    for path in all_paths:
        categories = path[0].split('/')
        if old_path != '':
            for old_cat in old_categories:
                if old_cat in categories:
                    try:
                        if categories[level] not in result:
                            result.append(categories[level])
                    except IndexError:
                        return 1
        else:
            try:
                if categories[level] not in result:
                    result.append(categories[level])
            except IndexError:
                return 1
    if '' in result:
        result.remove('')
    if result == []:
        return get_names_from_DB(old_path)
    return result


def get_names_from_DB(path: str) -> list:
    cursor.execute(
        "SELECT name FROM formuls WHERE path = ?",
        (path,)
    )
    names_from_db = cursor.fetchall()
    names = []
    for name in names_from_db:
        names.append(name[0])
    return names


def create_tables():
    # создаем таблицы в БД
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT,
        path TEXT,
        warns INT,
        is_banned BOOL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INT,
        nickname TEXT,
        password TEXT,
        in_admin BOOL,
        input_passwd BOOL,
        login BOOL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS formuls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        name TEXT,
        description TEXT,
        link TEXT,
        status TEXT
    )""")
    db.commit()


if __name__ == '__main__':
    pass
