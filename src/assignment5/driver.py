from pyspark.sql import SparkSession
from util import DriverUtil

def main():
    spark = SparkSession.builder \
        .appName("Employee Analysis DataFrame") \
        .getOrCreate()

    employee_schema = "employee_id INT, employee_name STRING, department STRING, State STRING, salary INT, Age INT"
    department_schema = "dept_id STRING, dept_name STRING"
    country_schema = "country_code STRING, country_name STRING"

    # Create DataFrames
    employee_df = spark.createDataFrame([
        (11, "james", "D101", "ny", 9000, 34),
        (12, "michel", "D101", "ny", 8900, 32),
        (13, "robert", "D102", "ca", 7900, 29),
        (14, "scott", "D103", "ca", 8000, 36),
        (15, "jen", "D102", "ny", 9500, 38),
        (16, "jeff", "D103", "uk", 9100, 35),
        (17, "maria", "D101", "ny", 7900, 40)
    ], schema=employee_schema)
    department_df = spark.createDataFrame([
        ("D101", "sales"),
        ("D102", "finance"),
        ("D103", "marketing"),
        ("D104", "hr"),
        ("D105", "support")
    ], schema=department_schema)
    country_df = spark.createDataFrame([
        ("ny", "newyork"),
        ("ca", "California"),
        ("uk", "Russia")
    ], schema=country_schema)

    # Find avg salary of each department
    avg_salary_df = employee_df.groupBy("department").agg(avg("salary").alias("avg_salary"))

    # Find employee's name and department name whose name starts with 'm'
    m_employees_df = employee_df.filter(col("employee_name").startswith("m")) \
                                .join(department_df, employee_df.department == department_df.dept_id, "inner") \
                                .select(employee_df["employee_name"], department_df["dept_name"])

    # Create a new column in employee_df as bonus by multiplying employee salary * 2
    employee_df = employee_df.withColumn("bonus", col("salary") * 2)

    # Reorder the column names of employee_df
    employee_df = employee_df.select("employee_id", "employee_name", "salary", "State", "Age", "department")

    # Join employee_df with department_df using inner, left, and right joins
    inner_join_df = employee_df.join(department_df, employee_df.department == department_df.dept_id, "inner")
    left_join_df = employee_df.join(department_df, employee_df.department == department_df.dept_id, "left")
    right_join_df = employee_df.join(department_df, employee_df.department == department_df.dept_id, "right")

    # Derive a new data frame with country_name instead of State in employee_df
    employee_country_df = employee_df.join(country_df, employee_df.State == country_df.country_code, "inner") \
                                      .drop("State") \
                                      .withColumnRenamed("country_name", "State")

    # Convert all the column names into lowercase from the result of question 7
    lowercase_df = employee_country_df.toDF(*(col_name.lower() for col_name in employee_country_df.columns))

    # Create external tables with parquet and CSV format
    DriverUtil.save_table_with_partition(lowercase_df, "employee.employee_details_parquet", ["State"])
    DriverUtil.save_table_as_csv(lowercase_df, "employee.employee_details_csv")

    spark.stop()

if __name__ == "__main__":
    main()
