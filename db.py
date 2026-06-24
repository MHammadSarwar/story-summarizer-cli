import sqlite3

def init_db():
    conn=sqlite3.connect("Summaries.db")
    cursor=conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Summaries(id INTEGER PRIMARY KEY AUTOINCREMENT, filepath varchar, summary text, max_words INTEGER, created_at DATETIME)")
    return conn

def save_summary(conn,filepath,summary,max_words,created_at):
    cursor=conn.cursor()
    cursor.execute("INSERT INTO Summaries (filepath, summary, max_words, created_at) VALUES(?,?,?,?)",(filepath,summary,max_words,created_at))
    conn.commit()
    
def get_history(conn,limit=10):
    cursor=conn.cursor()
    cursor.execute("SELECT * From Summaries ORDER BY id DESC LIMIT (?)",(limit,))
    result=cursor.fetchall()
    return result
    
    
if __name__ == "__main__":
    conn=init_db()
    save_summary(conn, "test path" , "test summary", 100, "00-00-0000 | 00:00")
    cursor=conn.cursor()
    cursor.execute("Select * FROM Summaries")
    print(cursor.fetchall())
    