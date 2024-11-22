"""”listing_user_relationship”

Revision ID: b6a7e1071ee5
Revises: 
Create Date: 2024-08-12 12:59:51.511533

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector  # Voeg deze regel toe



# revision identifiers, used by Alembic.
revision = 'b6a7e1071ee5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Maak een databaseverbinding
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Controleer of de tabel 'user' bestaat
    if 'user' in inspector.get_table_names():
        op.drop_table('user')

    # Controleer of de tabel 'listing' bestaat
    if 'listing' in inspector.get_table_names():
        op.drop_table('listing')


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'listing' not in inspector.get_table_names():
        op.create_table('listing',
            sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
            sa.Column('listing_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
            sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
            sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='listing_user_id_fkey'),
            sa.PrimaryKeyConstraint('id', name='listing_pkey')
        )
    if 'user' not in inspector.get_table_names():
        op.create_table('user',
            sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
            sa.Column('username', sa.VARCHAR(length=80), autoincrement=False, nullable=False),
            sa.PrimaryKeyConstraint('id', name='user_pkey'),
            sa.UniqueConstraint('username', name='user_username_key')
        )

