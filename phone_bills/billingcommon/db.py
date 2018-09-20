# Based on: https://github.com/mozilla/balrog/blob/v2.53/auslib/db.py

from datetime import datetime
from sqlalchemy import (
    between, create_engine, Column, DateTime, Integer, BigInteger,
    DECIMAL, ForeignKey, join, MetaData, null, select, String, Table, Time)
from sqlalchemy.orm import aliased


class BillingTable(object):
    def __init__(self, db, table, *args, **kwargs):
        self.db = db
        self.t = table
        for column in self.t.c:
            setattr(self, column.name, column)

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

    def select(self, where=None, limit=None):
        query = self.t.select(limit=limit)
        if where:
            for cond in where:
                query = query.where(cond)
        result = self.connection.execute(query)
        return self.to_dict(result)


class TariffConditionsTable(BillingTable):
    def __init__(self, db, metadata, IntegerType):
        table = Table(
            'tariff_conditions',
            metadata,
            Column('id', IntegerType, autoincrement=True, primary_key=True),
            Column('source_area_code', String, nullable=False),
            Column('destination_area_code', String, nullable=False),
            Column('start_at', Time, nullable=False),
            Column('end_at', Time, nullable=False))
        super().__init__(db, table)


class TariffConfigurationTable(BillingTable):
    def __init__(self, db, metadata, IntegerType, tariff_conditions_table):
        table = Table(
            'tariff_configuration',
            metadata,
            Column('id', IntegerType, autoincrement=True, primary_key=True),
            Column('created_date', DateTime, nullable=False),
            Column('config_start_date', DateTime, nullable=False),
            Column('config_end_date', DateTime),
            Column('conditions_id',
                    IntegerType,
                    ForeignKey(tariff_conditions_table.id),
                    nullable=False),
            Column('standard_charge', DECIMAL(8, 3, asdecimal=False), nullable=False),
            Column('call_time_charge', DECIMAL(8, 3, asdecimal=False), nullable=False))
        super().__init__(db, table)

    def get_current_configs(self, source_area_code, dest_area_code, timestamp):
        cfg_con_join = join(self.t, self.db.tariff_condition.t,
                 self.conditions_id == self.db.tariff_condition.id)
        columns = [
            self.id, self.standard_charge,
            self.call_time_charge,
            self.db.tariff_condition.id,
            self.db.tariff_condition.start_at,
            self.db.tariff_condition.end_at]
        query = select(columns).select_from(cfg_con_join)
        query = query.where(between(timestamp, self.config_start_date, self.config_end_date))
        query = query.where(self.db.tariff_condition.source_area_code == source_area_code)
        query = query.where(self.db.tariff_condition.destination_area_code == dest_area_code)
        configs = self.connection.execute(query).fetchall()
        configs = [{'config_id': config_id,
                    'standard_charge': standard_charge,
                    'call_time_charge': call_time_charge,
                    'condition_id': condition_id,
                    'start_at': start_at,
                    'end_at': end_at} for config_id,
                                          standard_charge,
                                          call_time_charge,
                                          condition_id,
                                          start_at,
                                          end_at in configs]
        return configs


class AppliedConfigTable(BillingTable):
    def __init__(self, db, metadata, IntegerType, call_records_table, tariff_conditions_table):
        table = Table(
            'applied_config',
            metadata,
            Column('call_id',
                    IntegerType,
                    ForeignKey(call_records_table.id),
                    primary_key=True),
            Column('config_id',
                   IntegerType,
                   ForeignKey(tariff_conditions_table.id),
                   primary_key=True),
            Column('order', Integer, nullable=False, primary_key=True),
            Column('start_at', DateTime, nullable=False),
            Column('end_at', DateTime, nullable=False),
            Column('standard_charge', DECIMAL(8, 3, asdecimal=False), nullable=False),
            Column('call_time_charge', DECIMAL(8, 3, asdecimal=False), nullable=False))
        super().__init__(db, table)


class CallRecordTable(BillingTable):
    def __init__(self, db, metadata, IntegerType, tariff_config_table):
        table = Table(
            'call_records',
            metadata,
            Column('id', IntegerType, autoincrement=True, primary_key=True),
            Column('created_date', DateTime, nullable=False),
            Column('external_id', IntegerType, nullable=False), # "id": Record unique identificator
            Column('call_id', String, nullable=False),
            Column('type', String, nullable=False),
            Column('source_area_code', String, nullable=True),
            Column('source', String, nullable=True),
            Column('destination_area_code', String, nullable=True),
            Column('destination', String, nullable=True),
            Column('timestamp', DateTime, nullable=False),
            Column('transaction_id', String))
        super().__init__(db, table)

    def insert(self, call_record):
        call_record['created_date'] = datetime.now()
        return super().insert(**call_record)

    def calls_for_pricing(self, area_code, phone_number, start_date, end_date):
        call_start_t = aliased(self.t)
        call_end_t = aliased(self.t)
        query_join = join(
            call_start_t, call_end_t,
            call_start_t.c.call_id == call_end_t.c.call_id)
        columns = [
            call_start_t.c.id.label('call_start_id'),
            call_start_t.c.call_id,
            call_start_t.c.destination_area_code.label('area_code'),
            call_start_t.c.destination.label('phone'),
            call_start_t.c.timestamp.label('start_at'),
            call_end_t.c.timestamp.label('end_at')
        ]
        query = select(columns).select_from(query_join)
        query = query.where(call_start_t.c.id != call_end_t.c.id)
        query = query.where(call_start_t.c.source_area_code == area_code)
        query = query.where(call_start_t.c.source == phone_number)
        query = query.where(between(call_end_t.c.timestamp, start_date, end_date))
        result = self.connection.execute(query).fetchall()
        calls = self.to_dict(result)
        for call in calls:
            configs = []
            where = [self.db.applied_config.call_id == call['call_start_id']]
            for config in self.db.applied_config.select(where=where):
                configs.append(config)
            call['configs'] = configs
        return calls


class BillingDb(object):
    def __init__(self, uri=None):
        if uri:
            self.setup(uri)

    def setup(self, uri):
        self.engine = create_engine(uri)
        self.metadata = MetaData(bind=self.engine)
        int_type = BigInteger
        if self.engine.name == 'sqlite':
            int_type = Integer
        self.tariff_conditions_table = TariffConditionsTable(self, self.metadata, int_type)
        self.tariff_config_table = TariffConfigurationTable(self, self.metadata, int_type, self.tariff_conditions_table)
        self.call_record_table = CallRecordTable(self, self.metadata, int_type, self.tariff_config_table)
        self.applied_config_table = AppliedConfigTable(self, self.metadata, int_type, self.call_record_table, self.tariff_config_table)

    @property
    def tariff_condition(self):
        return self.tariff_conditions_table

    @property
    def tariff_config(self):
        return self.tariff_config_table

    @property
    def call_record(self):
        return self.call_record_table

    @property
    def applied_config(self):
        return self.applied_config_table


def create_db(uri):
    return BillingDb(uri)
