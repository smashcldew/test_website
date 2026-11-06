"""把舊的 MongoDB（portfolio_db.projects）資料匯出成 D1 可執行的 SQL。

用法：
  $env:MONGO_URI="mongodb+srv://..."
  python mongo_to_d1.py              # 產生 migrate.sql
  python mongo_to_d1.py out.sql      # 自訂檔名

  cd ..
  npx wrangler d1 execute blog_backend --remote --file=scripts/migrate.sql

注意：
- 本腳本直接寫出 UTF-8 檔案。不要用 `> migrate.sql` 轉向，
  Windows 會改用 cp950 或 UTF-16 編碼，兩種都會失敗。
- 匯入前請確認 D1 的 projects 表是空的，否則資料會重複。
"""
import os
import sys

import pymongo


def sql_str(value):
    """轉成 SQL 字串常值，單引號 escape 成兩個單引號。"""
    if value is None:
        return "''"
    return "'" + str(value).replace("'", "''") + "'"


def main():
    uri = os.getenv("MONGO_URI")
    if not uri:
        sys.exit("請先設定環境變數 MONGO_URI")

    out_path = sys.argv[1] if len(sys.argv) > 1 else "migrate.sql"
    collection = pymongo.MongoClient(uri)["portfolio_db"]["projects"]

    count = 0
    # 依 find() 的順序寫出，D1 的 id 會和舊的索引順序一致
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        for doc in collection.find():
            f.write(
                "INSERT INTO projects (title, image, content, date) VALUES ("
                f"{sql_str(doc.get('title'))}, {sql_str(doc.get('image'))}, "
                f"{sql_str(doc.get('content'))}, {sql_str(doc.get('date'))});\n"
            )
            count += 1

    print(f"已寫出 {count} 筆資料到 {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
