from sqlalchemy import *
from migrate import *

def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    call_records = Table('call_records', metadata, autoload=True)
    tariff_configuration = Table('tariff_configuration', metadata, autoload=True)

    fk = ForeignKeyConstraint(
        [call_records.c.applied_tariff_config],
        [tariff_configuration.c.id])
    fk.drop()

    applied_config = Table(
        'applied_config',
        metadata,
        Column(
            'call_id',
            BigInteger,
            ForeignKey(call_records.c.id),
            primary_key=True),
        Column(
            'config_id',
            BigInteger,
            ForeignKey(tariff_configuration.c.id),
            primary_key=True),
        Column('start_time', Time, nullable=False),
        Column('end_time', Time, nullable=False),
        Column('standard_charge', DECIMAL(8, 3), nullable=False),
        Column('call_time_charge', DECIMAL(8, 3), nullable=False),
        Column('order', Integer, nullable=False))
    applied_config.create()


def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)

    applied_config = Table('applied_config', metadata, autoload=True)
    applied_config.drop()

    call_records = Table('call_records', metadata, autoload=True)
    tariff_configuration = Table('tariff_configuration', metadata, autoload=True)

    fk = ForeignKeyConstraint(
        [call_records.c.applied_tariff_config],
        [tariff_configuration.c.id])
    fk.create()
