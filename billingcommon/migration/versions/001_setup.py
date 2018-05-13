from sqlalchemy import Table, BigInteger, Column, Integer, String, DateTime, DECIMAL, ForeignKey, MetaData


meta = MetaData()


tariff_conditions = Table(
    'tariff_conditions',
    meta,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('start_date', DateTime, nullable=False),
    Column('end_date', DateTime, nullable=False))


tariff_configuration = Table(
    'tariff_configuration',
    meta,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('conditions_id',
            Integer,
            ForeignKey(tariff_conditions.c.id),
            nullable=False),
    Column('created_date', DateTime, nullable=False),
    Column('start_date', DateTime, nullable=False),
    Column('end_date', DateTime),
    Column('standard_charge', DECIMAL(8, 3), nullable=False),
    Column('time_units', Integer, nullable=False),
    Column('call_time_charge', DECIMAL(8, 3), nullable=False))


call_entries = Table(
    'call_entries',
    meta,
    Column('id', BigInteger, autoincrement=True, primary_key=True),
    Column('created_date', DateTime, nullable=False),
    Column('external_id', String, nullable=False), # "id": Record unique identificator
    Column('call_id', String, nullable=False),
    Column('type', String, nullable=False),
    Column('source', String, nullable=False),
    Column('destination', String, nullable=False),
    Column('timestamp', DateTime, nullable=False),
    Column('standard_charge', DECIMAL(8, 3), nullable=False),
    Column('time_units', Integer, nullable=False),
    Column('call_time_charge', DECIMAL(8, 3), nullable=False),
    Column('charge_reference', String),
    Column('charge_conditions_reference', String))


def upgrade(migrate_engine):
    meta.bind = migrate_engine
    tariff_conditions.create()
    tariff_configuration.create()
    call_entries.create()


def downgrade(migrate_engine):
    raise NotImplementedError('Setup script')
