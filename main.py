from fastmcp import FastMCP
import os
import sqlite3

# Define the path to the SQLite database file in the same directory as this script
DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')

# Initialize the FastMCP server with a name
mcp = FastMCP("ExpenseTracker")


def init_db():
    """Initialize the database by creating the expenses table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        # Create the expenses table with all necessary columns
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
            '''
        )


# Initialize the database when the module is loaded
init_db()


@mcp.tool()
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
) -> dict:
    """Add a new expense to the database.
    Args:
        date: Date of the expense (e.g., '2024-12-29')
        amount: Amount spent
        category: Main category of the expense
        subcategory: Optional subcategory
        note: Optional note about the expense
    Returns:
        Dictionary with status and the new expense ID
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Insert the expense record into the database
        cur = conn.execute(
            '''
            INSERT INTO expenses (date, amount, category, subcategory, note)
            VALUES (?, ?, ?, ?, ?)
            ''',
            (date, amount, category, subcategory, note)
        )
        # Return success status and the ID of the newly inserted record
        return {"status": "success", "id": cur.lastrowid}


@mcp.tool()
def list_expenses() -> list:
    """List all expenses from the database ordered by ID.
    Returns:
        List of dictionaries, each containing an expense record
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Query all expenses ordered by ID
        cur = conn.execute(
            'SELECT id, date, amount, category, subcategory, note FROM expenses ORDER BY id ASC'
        )
        # Get column names from the cursor description
        cols = [description[0] for description in cur.description]
        # Convert each row to a dictionary with column names as keys
        return [dict(zip(cols, row)) for row in cur.fetchall()]


@mcp.tool()
def edit_expense(
    expense_id: int,
    date: str = None,
    amount: float = None,
    category: str = None,
    subcategory: str = None,
    note: str = None
) -> dict:
    """Edit an existing expense in the database.
    Args:
        expense_id: ID of the expense to edit
        date: New date of the expense (optional)
        amount: New amount spent (optional)
        category: New main category of the expense (optional)
        subcategory: New subcategory (optional)
        note: New note about the expense (optional)
    Returns:
        Dictionary with status and message
    """
    with sqlite3.connect(DB_PATH) as conn:
        # First check if the expense exists
        cur = conn.execute(
            'SELECT COUNT(*) FROM expenses WHERE id = ?',
            (expense_id,)
        )
        if cur.fetchone()[0] == 0:
            return {"status": "error", "message": f"Expense with ID {expense_id} not found"}

        # Build the update query dynamically based on provided fields
        fields = []
        values = []

        if date is not None:
            fields.append("date = ?")
            values.append(date)
        if amount is not None:
            fields.append("amount = ?")
            values.append(amount)
        if category is not None:
            fields.append("category = ?")
            values.append(category)
        if subcategory is not None:
            fields.append("subcategory = ?")
            values.append(subcategory)
        if note is not None:
            fields.append("note = ?")
            values.append(note)

        if not fields:
            return {"status": "warning", "message": "No changes made - no fields provided"}

        # Add expense_id to the end of values list
        values.append(expense_id)

        # Execute the update query
        query = f"UPDATE expenses SET {', '.join(fields)} WHERE id = ?"
        conn.execute(query, values)

        return {"status": "success", "message": f"Expense {expense_id} updated successfully"}


@mcp.tool()
def delete_expense(expense_id: int) -> dict:
    """Delete an expense from the database.
    Args:
        expense_id: ID of the expense to delete
    Returns:
        Dictionary with status and message
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Check if expense exists before deleting
        cur = conn.execute(
            'SELECT COUNT(*) FROM expenses WHERE id = ?',
            (expense_id,)
        )
        if cur.fetchone()[0] == 0:
            return {"status": "error", "message": f"Expense with ID {expense_id} not found"}

        # Delete the expense
        conn.execute(
            'DELETE FROM expenses WHERE id = ?',
            (expense_id,)
        )
        return {"status": "success", "message": f"Expense {expense_id} deleted successfully"}


@mcp.tool()
def summarize_expenses() -> dict:
    """Summarize total expenses by category.
    Returns:
        Dictionary with summary statistics including total and breakdown by category
    """
    with sqlite3.connect(DB_PATH) as conn:
        # Get total amount across all categories
        cur = conn.execute('SELECT SUM(amount) FROM expenses')
        total = cur.fetchone()[0] or 0

        # Get breakdown by category
        cur = conn.execute(
            '''
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
            '''
        )
        by_category = {row[0]: row[1] for row in cur.fetchall()}

        return {
            "total": total,
            "by_category": by_category
        }


# Run the MCP server when the script is executed directly
if __name__ == "__main__":
    mcp.run(transport='sse', host='0.0.0.0', port=8000)