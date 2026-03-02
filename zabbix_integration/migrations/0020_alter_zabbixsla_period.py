from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zabbix_integration', '0019_zabbixevent_value'),  # mantenha o dependency correto
    ]

    operations = [
        migrations.RunSQL(
            """
            ALTER TABLE zabbix_integration_zabbixsla
            ALTER COLUMN period
            TYPE timestamp with time zone
            USING to_timestamp(period);
            """,
            reverse_sql="""
            ALTER TABLE zabbix_integration_zabbixsla
            ALTER COLUMN period
            TYPE bigint
            USING EXTRACT(EPOCH FROM period);
            """
        ),
    ]