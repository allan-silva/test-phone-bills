from sqlalchemy import Table, BigInteger, Column, Integer, String, DateTime, DECIMAL, Time, ForeignKey, MetaData


meta = MetaData()


tariff_conditions = Table(
    'tariff_conditions',
    meta,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('source_area_code', String, nullable=False),
    Column('destination_area_code', String, nullable=False),
    Column('start_at', Time, nullable=False),
    Column('end_at', Time, nullable=False))


tariff_configuration = Table(
    'tariff_configuration',
    meta,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('created_date', DateTime, nullable=False),
    Column('config_start_date', DateTime, nullable=False),
    Column('config_end_date', DateTime),
    Column('conditions_id',
            Integer,
            ForeignKey(tariff_conditions.c.id),
            nullable=False),
    Column('standard_charge', DECIMAL(8, 3), nullable=False),
    Column('call_time_charge', DECIMAL(8, 3), nullable=False))


call_records = Table(
    'call_records',
    meta,
    Column('id', BigInteger, autoincrement=True, primary_key=True),
    Column('created_date', DateTime, nullable=False),
    Column('external_id', String, nullable=False), # "id": Record unique identificator
    Column('call_id', String, nullable=False),
    Column('type', String, nullable=False),
    Column('source_area_code', String, nullable=False),
    Column('source', String, nullable=False),
    Column('destination_area_code', String, nullable=False),
    Column('destination', String, nullable=False),
    Column('timestamp', DateTime, nullable=False))


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    tariff_conditions.create()
    tariff_configuration.create()
    call_records.create()


def downgrade(migrate_engine):
    meta.bind = migrate_engine
    call_records.drop()
    tariff_configuration.drop()
    tariff_conditions.drop()


