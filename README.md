# SQLAlchemy Practice

## 📌 Description
This project is educational and demonstrates the **basics+** of working with SQLAlchemy for database management in Python. It covers key ORM features such as:
- Creating tables
- Performing CRUD operations
- Working with queries and subqueries
- Relationships (all types)
- Query and request optimization

The functionality described below is implemented in both **Synchronous and Asynchronous** versions, as well as using both **Declarative and Imperative** programming styles (`orm.py` / `core.py`).

---
## ⚙️ Functionality

### 🔹 1. Creating Tables
- **`create_tables()`**: Creates all tables defined in the ORM models based on the connected database engine. Before creation, all existing tables are deleted.

### 🔹 2. Adding Data
- **`insert_workers()`**: Adds workers to the database.
- **`insert_resumes()`**: Adds worker resumes.
- **`insert_additional_resumes()`**: Adds additional data about workers and their resumes.

### 🔹 3. Reading Data
- **`select_workers()`**: Retrieves all workers from the database.
- **`select_resumes_avg_compensation(like_language)`**: Calculates the average salary for a specific programming language for each type of employment.
- **`select_workers_with_lazy_relationship()`**: Demonstrates the "N+1" query problem.
- **`select_workers_with_joined_relationship()`**: Uses `joinedload()` for query optimization.
- **`select_workers_with_selectin_relationship()`**: Applies `selectinload()` for one-to-many relationships.
- **`select_workers_with_condition_relationship()`**: Loads only selected relationships.
- **`select_workers_with_condition_relationship_contains_eager()`**: Uses `contains_eager()` for selective relationships.
- **`select_workers_with_condition_relationship_contains_eager_with_limit()`**: Demonstrates the use of subqueries and `limit()` for selective results.

### 🔹 4. Updating Data
- **`update_worker(worker_id, new_username)`**: Updates the username for a given worker ID.

### 🔹 5. Using Complex Queries
- **`join_cte_subquery_window_func()`**: Demonstrates the use of CTE (Common Table Expressions), subqueries, and window functions for salary analysis.

---
## 🚀 Installation & Execution

### 1️⃣ Install Dependencies
Ensure you have all necessary packages installed by running:
```bash
pip install -r requirements_v2.txt
```

### 2️⃣ Configure Database Connection
The application uses **PostgreSQL**. Update the `.env` file with your database credentials:
```plaintext
DB_HOST=your_host  
DB_PORT=your_port  
DB_USER=your_user  
DB_PASS=your_password  
DB_NAME=your_database  
```

### 3️⃣ Run the Application
Execute the script with the appropriate flags to run **synchronous or asynchronous** operations using either raw SQL (`core`) or ORM (`orm`):

#### 🔹 **Synchronous Execution**
- Using raw SQL:
  ```bash
  python main.py --core --sync
  ```
- Using ORM:
  ```bash
  python main.py --orm --sync
  ```

#### 🔹 **Asynchronous Execution**
- Using raw SQL:
  ```bash
  python main.py --core --async
  ```
- Using ORM:
  ```bash
  python main.py --orm --async
  ```

### 🌐 Running the Web Server
To start the **FastAPI web server**, use:
```bash
python main.py --webserver
```
This will launch a **FastAPI** instance with endpoints to retrieve worker and resume data.

---
💡 **Happy Coding!** 🚀
