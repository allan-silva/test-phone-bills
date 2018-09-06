area_codes = ['11', '41', '61', '68', '99']


def get_insert_conditions():
    time_ranges = [('06:00:00', '21:59:59'), ('22:00:00', '05:59:59')]
    for start_at, end_at in time_ranges:
        for area_code_source in area_codes:
            for area_code_dest in area_codes:
                yield f"""insert into tariff_conditions(
                            source_area_code, destination_area_code, start_at, end_at)
                          values ('{area_code_source}', '{area_code_dest}', '{start_at}', '{end_at}');"""


def get_insert_configs():
    for area_code_source in area_codes:
        for area_code_dest in area_codes:
            yield f"""insert into tariff_configuration(
                        created_date, config_start_date, conditions_id,
                        standard_charge, call_time_charge)
                      select
                        now(), now(), c.id, '0.36', '0.09'
                      from tariff_conditions c
                      where
                        c.start_at = '06:00:00'
                        and
                        c.source_area_code = '{area_code_source}'
                        and
                        c.destination_area_code = '{area_code_dest}';"""
            yield f"""insert into tariff_configuration(
                        created_date, config_start_date, conditions_id,
                        standard_charge, call_time_charge)
                      select
                        now(), now(), c.id, '0.36', '0.0'
                      from tariff_conditions c
                      where
                        c.start_at = '22:00:00'
                        and
                        c.source_area_code = '{area_code_source}'
                        and
                        c.destination_area_code = '{area_code_dest}';"""


def upgrade(migrate_engine):
    conn = migrate_engine.connect()
    for ins in get_insert_conditions():
        conn.execute(ins)
    for ins in get_insert_configs():
        conn.execute(ins)


def downgrade(migrate_engine):
    conn = migrate_engine.connect()
    conn.execute('delete from tariff_configuration;')
    conn.execute('delete from tariff_conditions;')
