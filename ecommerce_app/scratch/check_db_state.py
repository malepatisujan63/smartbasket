import sqlite3, os

db_path = r"d:\3rd sem created files\AIML PROJECT\ecommerce_app\fast_ecommerce.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM Users")
print(f"Total Users: {c.fetchone()[0]}")

c.execute("SELECT user_id, username FROM Users WHERE username LIKE 'p%' ORDER BY user_id")
personas = c.fetchall()
print(f"Total Persona Users (p001-p100): {len(personas)}")
if personas:
    print(f"  First: {personas[0]}")
    print(f"  Last:  {personas[-1]}")

c.execute("SELECT action, COUNT(*) FROM UserLogs GROUP BY action")
print("UserLogs by action:", c.fetchall())

# Check how many logs each persona has
c.execute("""
    SELECT u.user_id, u.username, 
           COUNT(l.log_id) as total_logs,
           SUM(CASE WHEN l.action = 'view' THEN 1 ELSE 0 END) as view_logs
    FROM Users u
    LEFT JOIN UserLogs l ON u.user_id = l.user_id
    WHERE u.username LIKE 'p%'
    GROUP BY u.user_id
    ORDER BY u.user_id
""")
persona_stats = c.fetchall()
print(f"Personas with logs: {len([p for p in persona_stats if p[2] > 0])}")
print("Sample persona stats (first 5):")
for p in persona_stats[:5]:
    print(f"  User {p[0]} ({p[1]}): {p[2]} total logs, {p[3]} view logs")

conn.close()
