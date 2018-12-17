import pandas as pd
from sqlalchemy import create_engine


class BankingDatabase(object):

    def __init__(self, user, password, host, port, database_name):
        # ====== Connection ======
        # Connecting to PostgreSQL by providing a sqlachemy engine
        self.engine = create_engine(
            'postgresql://' + user + ':' + password + '@' + host + ':' + port + '/' + database_name, echo=False)

    def create_or_append_table(self, dataframe, table_name, mode='append'):
        dataframe.to_sql(name=table_name, con=self.engine, if_exists=mode, index=False)

    def read_from_db(self, query):
        # ====== Reading table ======
        # Reading PostgreSQL table into a pandas DataFrame
        data = pd.read_sql(query, self.engine)
        return data
