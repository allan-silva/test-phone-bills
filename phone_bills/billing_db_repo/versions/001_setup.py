from sqlalchemy import Table, BigInteger, Column, String, DateTime, DECIMAL, Time, ForeignKey, MetaData


meta = MetaData()


tariff_conditions = Table(
    'tariff_conditions',
    meta,
    Column('id', BigInteger, autoincrement=True, primary_key=True),
    Column('source_area_code', String, nullable=False),
    Column('destination_area_code', String, nullable=False),
    Column('start_at', Time, nullable=False),
    Column('end_at', Time, nullable=False))


tariff_configuration = Table(
    'tariff_configuration',
    meta,
    Column('id', BigInteger, autoincrement=True, primary_key=True),
    Column('created_date', DateTime, nullable=False),
    Column('config_start_date', DateTime, nullable=False),
    Column('config_end_date', DateTime),
    Column('conditions_id',
           BigInteger,
           ForeignKey(tariff_conditions.c.id),
           nullable=False),
    Column('standard_charge', DECIMAL(8, 3), nullable=False),
    Column('call_time_charge', DECIMAL(8, 3), nullable=False))


call_records = Table(
    'call_records',
    meta,
    Column('id', BigInteger, autoincrement=True, primary_key=True),
    Column('created_date', DateTime, nullable=False),
    Column('external_id', BigInteger, nullable=False),  # "id": Record unique identificator
    Column('call_id', BigInteger, nullable=False),
    Column('type', String, nullable=False),
    Column('source_area_code', String, nullable=True),
    Column('source', String, nullable=True),
    Column('destination_area_code', String, nullable=True),
    Column('destination', String, nullable=True),
    Column('timestamp', DateTime, nullable=False),
    Column('applied_tariff_config',
           BigInteger,
           ForeignKey(tariff_configuration.c.id),
           nullable=True))


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
