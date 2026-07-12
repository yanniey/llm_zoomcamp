from dataclasses import dataclass

from db_init import get_db_connection
from metrics import LLMCallRecord


# a dataclass for the stats for streamlit dashboard
@dataclass
class Stats:
    total: int
    avg_response_time: float
    total_cost: float
    avg_tokens: float


# a function to compute agg stats
def get_stats():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                  COUNT(*),
                  AVG(response_time),
                  SUM(cost),
                  AVG(total_tokens)
                FROM LLMCallRecords
            """)
            row = cur.fetchone()
    finally:
        conn.close()
    return Stats(
        total=row[0],
        avg_response_time=row[1],
        total_cost=row[2],
        avg_tokens=row[3],
    )


# A query returns each row as a plain tuple. You have to remember that column 4 is the model and column 6 is the prompt.
# We convert each row back into the LLMCallRecord dataclass we already use for live calls.
# A helper function to convert a database row into an LLMCallRecord
def row_to_record(row):
    return LLMCallRecord(
        model=row[4],
        prompt=row[6],
        instructions=row[5],
        answer=row[2],
        prompt_tokens=row[7],
        completion_tokens=row[8],
        total_tokens=row[9],
        response_time=row[10],
        cost=row[11],
        timestamp=row[12],
    )


def get_conversations(limit=5):
    """get the top 5 most recent calls"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, question, answer, course, model,
                       instructions, prompt,
                       prompt_tokens, completion_tokens, total_tokens,
                       response_time, cost, timestamp
                FROM LLMCallRecords
                ORDER BY timestamp DESC 
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()  # this returns a tuple
    finally:
        conn.close()

    return [row_to_record(row) for row in rows]


def get_relevance_stats() -> dict[str, int]:
    """Count judge-rated feedback rows by relevance label.

    e.g. {'RELEVANT': 12, 'PARTLY_RELEVANT': 3}
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT relevance, COUNT(*)
                FROM feedback
                WHERE source = 'judge'
                GROUP BY relevance
            """)
            rows = cur.fetchall()
    finally:
        conn.close()
    return dict(rows)


def get_user_feedback_stats():
    """show all user feedbacks, +1 or -1"""
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    SUM(CASE WHEN score > 0 THEN 1 ELSE 0 END),
                    SUM(CASE WHEN score < 0 THEN 1 ELSE 0 END)
                FROM feedback
                WHERE source = 'user'
            """)
            row = cur.fetchone()
    finally:
        conn.close()
    return row


if __name__ == "__main__":
    records = get_conversations()
    for record in records:
        print(record)
