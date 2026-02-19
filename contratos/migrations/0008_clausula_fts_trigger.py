from django.db import migrations
from django.contrib.postgres.indexes import GinIndex

class Migration(migrations.Migration):
    dependencies = [
        ("contratos", "0007_contratoclausula_search_vector"),
    ]

    operations = [
        migrations.RunSQL(
            sql=r"""
            CREATE EXTENSION IF NOT EXISTS unaccent;

            CREATE FUNCTION contratos_clausula_tsvector_update() RETURNS trigger AS $$
            BEGIN
              NEW.search_vector :=
                setweight(to_tsvector('portuguese', unaccent(coalesce(NEW.numero, ''))), 'A') ||
                setweight(to_tsvector('portuguese', unaccent(coalesce(NEW.titulo, ''))), 'A') ||
                setweight(to_tsvector('portuguese', unaccent(coalesce(NEW.texto, ''))), 'B');
              RETURN NEW;
            END
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS contratos_clausula_tsvector_trigger ON contratos_contratoclausula;

            CREATE TRIGGER contratos_clausula_tsvector_trigger
            BEFORE INSERT OR UPDATE OF numero, titulo, texto
            ON contratos_contratoclausula
            FOR EACH ROW EXECUTE FUNCTION contratos_clausula_tsvector_update();

            UPDATE contratos_contratoclausula
            SET search_vector =
                setweight(to_tsvector('portuguese', unaccent(coalesce(numero, ''))), 'A') ||
                setweight(to_tsvector('portuguese', unaccent(coalesce(titulo, ''))), 'A') ||
                setweight(to_tsvector('portuguese', unaccent(coalesce(texto, ''))), 'B');
            """,
            reverse_sql=r"""
            DROP TRIGGER IF EXISTS contratos_clausula_tsvector_trigger ON contratos_contratoclausula;
            DROP FUNCTION IF EXISTS contratos_clausula_tsvector_update();
            """,
        ),
        migrations.AddIndex(
            model_name="contratoclausula",
            index=GinIndex(fields=["search_vector"], name="clausula_fts_gin"),
        ),
    ]
