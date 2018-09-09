from sqlalchemy import Table, Column, MetaData, String


def upgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    call_record_table = Table('call_records', metadata, autoload=True)
    transaction_id = Column('transaction_id', String)
    transaction_id.create(call_record_table)



def downgrade(migrate_engine):
    metadata = MetaData(bind=migrate_engine)
    call_record_table = Table('call_records', metadata, autoload=True)
    call_record_table.c.transaction_id.drop()
