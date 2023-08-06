import duckdb
import pandas as pd
from langchain import LLMChain, PromptTemplate

from sayql.prompt import DEFAULT_PROMPT

# Will need to abstract for multiple datastores
#   dfs are actually "tables" in duckdb, so will need to
#   account for that eventually
# Data should be arbitrary collection of tables


# TODO: allow for lazy execution chaining
# TODO: abstraction for LLM class, maybe via langchain?
# TODO better API key handling


class SayQL:
    def __init__(self, df: pd.DataFrame, llm):
        self.df = df
        self.llm = llm

    def _serialize_df_schema(self):
        # [question] | [db_id] | [table] : [column] ( [content] , [content] ) , [column] ( ... ) , [...] | [table] : ... | ...
        columns: list[str] = self.df.columns.to_list()
        col_string: str = ",".join(columns)
        return f"df:{col_string}"

    def _to_sql(self, query: str) -> str:
        prompt: str = PromptTemplate(
            template=DEFAULT_PROMPT, input_variables=["schema_str", "query"]
        )
        schema_str: str = self._serialize_df_schema()
        llm_chain = LLMChain(llm=self.llm, prompt=prompt)
        return llm_chain.predict(query=query, schema_str=schema_str)

    def query(self, query: str) -> pd.DataFrame:
        sql: str = self._to_sql(query)
        # global naming for duckdb
        df = self.df
        return duckdb.query(sql).df()
