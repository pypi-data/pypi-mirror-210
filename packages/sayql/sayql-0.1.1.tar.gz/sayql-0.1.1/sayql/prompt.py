DEFAULT_PROMPT = """You will need to return a valid DuckDB SQL query given the following user query and serialized schema string.
    The serialized SQL string will have the following format:

    [question] | [db_id] | [table] : [column] ( [content] , [content] ) , [column] ( ... ) , [...] | [table] : ... | ...

    You must parse this format and generate a valid SQL query that satisfies the user query. DO NOT generate any thing other than SQL!

    Example:

    SCHEMA:
    df:country,capital,continent,population,area

    USER QUERY:
    What is the capital of India?

    OUTPUT SQL:
    SELECT capital FROM df WHERE country = 'India'

    ---

    SCHEMA:
    {schema_str}

    USER QUERY:
    {query}

    OUTPUT SQL:"""

