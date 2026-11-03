import os
import database

def backup():
    conn, eng = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SHOW TABLES')
    tables = [r[0] for r in cursor.fetchall()]

    backup_path = os.path.join(os.path.dirname(__file__), 'database', 'backup_financial_manager.sql')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write('-- FINORA AUTOMATIC SAFETY BACKUP --\n')
        f.write('SET FOREIGN_KEY_CHECKS = 0;\n\n')
        for t in tables:
            cursor.execute(f'SHOW CREATE TABLE `{t}`')
            create_sql = cursor.fetchone()[1]
            f.write(f'DROP TABLE IF EXISTS `{t}`;\n')
            f.write(f'{create_sql};\n\n')

            cursor.execute(f'SELECT * FROM `{t}`')
            rows = cursor.fetchall()
            if rows:
                cursor.execute(f'SHOW COLUMNS FROM `{t}`')
                cols = [f'`{c[0]}`' for c in cursor.fetchall()]
                cols_str = ', '.join(cols)
                for row in rows:
                    vals = []
                    for val in row:
                        if val is None:
                            vals.append('NULL')
                        elif isinstance(val, (int, float)):
                            vals.append(str(val))
                        else:
                            s = str(val).replace('\\', '\\\\').replace("'", "\\'")
                            vals.append(f"'{s}'")
                    vals_str = ', '.join(vals)
                    f.write(f'INSERT INTO `{t}` ({cols_str}) VALUES ({vals_str});\n')
                f.write('\n')
        f.write('SET FOREIGN_KEY_CHECKS = 1;\n')

    cursor.close()
    conn.close()
    print('Backup completed:', backup_path, 'Size:', os.path.getsize(backup_path), 'bytes')

if __name__ == '__main__':
    backup()
