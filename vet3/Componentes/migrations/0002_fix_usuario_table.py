from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Componentes', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DROP TABLE IF EXISTS Componentes_usuario CASCADE;
            
            CREATE TABLE Componentes_usuario (
                id BIGSERIAL PRIMARY KEY,
                password VARCHAR(128) NOT NULL,
                last_login TIMESTAMP WITH TIME ZONE,
                is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
                username VARCHAR(30) NOT NULL UNIQUE,
                first_name VARCHAR(150) NOT NULL DEFAULT '',
                last_name VARCHAR(150) NOT NULL DEFAULT '',
                email VARCHAR(50) NOT NULL DEFAULT '',
                is_staff BOOLEAN NOT NULL DEFAULT FALSE,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                date_joined TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                rol VARCHAR(20) NOT NULL DEFAULT 'recepcionista',
                telefono VARCHAR(15) NOT NULL DEFAULT ''
            );
            
            CREATE TABLE IF NOT EXISTS Componentes_usuario_groups (
                id BIGSERIAL PRIMARY KEY,
                usuario_id BIGINT NOT NULL REFERENCES Componentes_usuario(id) ON DELETE CASCADE,
                group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
                UNIQUE(usuario_id, group_id)
            );
            
            CREATE TABLE IF NOT EXISTS Componentes_usuario_user_permissions (
                id BIGSERIAL PRIMARY KEY,
                usuario_id BIGINT NOT NULL REFERENCES Componentes_usuario(id) ON DELETE CASCADE,
                permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
                UNIQUE(usuario_id, permission_id)
            );
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS Componentes_usuario CASCADE;
            CREATE TABLE Componentes_usuario (
                IdUsuario BIGSERIAL PRIMARY KEY,
                nombre VARCHAR(30) NOT NULL,
                password VARCHAR(50) NOT NULL
            );
            """
        ),
    ]
