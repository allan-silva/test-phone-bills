from sqlalchemy import (
    create_engine, Column, DateTime, Integer, MetaData, Table)


class BillingTable(object):
    def __init__(self, *args, **kwargs):
        self.t = self.table

    def to_dict(self, result):
        d = []
        for r in result:
            d.append(dict(r))
        return d

    @property
    def engine(self):
        return self.t.metadata.bind

    @property
    def connection(self):
        return self.engine.connect()

    def get_transaction(self):
        return self.connection.begin()

    def execute(self, sttm):
        return self.connection.execute(sttm)

    def insert(self, **values):
        with self.get_transaction() as transaction:
            try:
                sttm = self.t.insert(values=values)
                ret = self.execute(sttm)
                transaction.commit()
                pk = {'id': ret.inserted_primary_key[0]}
                pk.update(ret.last_inserted_params())
                return pk
            except Exception as e:
                transaction.rollback()
                raise e

    def select(self, where=None):
        query = self.t.select()
        if where:
            for cond in where:
                query = query.where(cond)
        result = self.connection.execute(query)

        return self.to_dict(result)


class TariffConditionsTable(BillingTable):
    def __init__(self, metadata):
        self.table = Table(
            'tariff_conditions',
            metadata,
            Column('id', Integer, autoincrement=True, primary_key=True),
            Column('start_date', DateTime, nullable=False),
            Column('end_date', DateTime, nullable=False))
        super().__init__()


class BillingDb(object):
    def __init__(self, uri=None):
        if uri:
            self.setup(uri)

    def setup(self, uri):
        self.engine = create_engine(uri)
        self.metadata = MetaData(bind=self.engine)

        self.tariff_conditions_table = TariffConditionsTable(self.metadata)

    @property
    def tariff_conditions(self):
        return self.tariff_conditions_table


def create_db(uri):
    return BillingDb(uri)
