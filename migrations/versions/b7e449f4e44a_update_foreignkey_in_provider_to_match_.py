"""Update ForeignKey in Provider to match User column name

Revision ID: b7e449f4e44a
Revises: b6a7e1071ee5
Create Date: 2024-11-28 18:34:28.935983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7e449f4e44a'
down_revision = 'b6a7e1071ee5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Customer', schema=None) as batch_op:
        batch_op.alter_column('PhoneC',
               existing_type=sa.BIGINT(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)

    with op.batch_alter_table('Listing', schema=None) as batch_op:
        batch_op.alter_column('ListingID',
               existing_type=sa.BIGINT(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
        batch_op.alter_column('NameTool',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=False)

    with op.batch_alter_table('Provider', schema=None) as batch_op:
        batch_op.alter_column('providerp',
               existing_type=sa.BIGINT(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
        batch_op.drop_constraint('Provider_phoneP_key', type_='unique')

    with op.batch_alter_table('Transactie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('listingID', sa.BigInteger(), nullable=False))
        batch_op.alter_column('Commission fee',
               existing_type=sa.REAL(),
               type_=sa.Float(),
               existing_nullable=True)
        batch_op.alter_column('Date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
        batch_op.drop_constraint('Transactie_ListingID_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Listing', ['listingID'], ['ListingID'])
        batch_op.drop_column('ListingID')

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.alter_column('Address',
               existing_type=sa.VARCHAR(),
               type_=sa.Text(),
               existing_nullable=False)
        batch_op.create_unique_constraint(None, ['Phone_number'])
        batch_op.drop_column('id')

    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.alter_column('ReviewID',
               existing_type=sa.BIGINT(),
               server_default=None,
               existing_nullable=False,
               autoincrement=True)
        batch_op.alter_column('date',
               existing_type=sa.DATE(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.alter_column('date',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.alter_column('ReviewID',
               existing_type=sa.BIGINT(),
               server_default=sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
               existing_nullable=False,
               autoincrement=True)

    with op.batch_alter_table('User', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.BIGINT(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.alter_column('Address',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=False)

    with op.batch_alter_table('Transactie', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ListingID', sa.BIGINT(), sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), autoincrement=True, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Transactie_ListingID_fkey', 'Listing', ['ListingID'], ['ListingID'])
        batch_op.alter_column('Date',
               existing_type=sa.DateTime(timezone=True),
               type_=sa.DATE(),
               existing_nullable=True)
        batch_op.alter_column('Commission fee',
               existing_type=sa.Float(),
               type_=sa.REAL(),
               existing_nullable=True)
        batch_op.drop_column('listingID')

    with op.batch_alter_table('Provider', schema=None) as batch_op:
        batch_op.create_unique_constraint('Provider_phoneP_key', ['providerp'])
        batch_op.alter_column('providerp',
               existing_type=sa.BIGINT(),
               server_default=sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
               existing_nullable=False,
               autoincrement=True)

    with op.batch_alter_table('Listing', schema=None) as batch_op:
        batch_op.alter_column('NameTool',
               existing_type=sa.Text(),
               type_=sa.VARCHAR(),
               existing_nullable=False)
        batch_op.alter_column('ListingID',
               existing_type=sa.BIGINT(),
               server_default=sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
               existing_nullable=False,
               autoincrement=True)

    with op.batch_alter_table('Customer', schema=None) as batch_op:
        batch_op.alter_column('PhoneC',
               existing_type=sa.BIGINT(),
               server_default=sa.Identity(always=False, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1),
               existing_nullable=False,
               autoincrement=True)

    # ### end Alembic commands ###
