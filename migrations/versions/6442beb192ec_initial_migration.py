"""Initial migration

Revision ID: 6442beb192ec
Revises: 
Create Date: 2024-10-21 21:10:57.874141

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6442beb192ec'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_item')
    op.drop_table('table')
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('venue_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('total_price',
               existing_type=mysql.FLOAT(),
               nullable=False)
        batch_op.drop_constraint('order_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])
        batch_op.drop_column('customer_id')
        batch_op.drop_column('status')

    with op.batch_alter_table('tables', schema=None) as batch_op:
        batch_op.alter_column('is_available',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
        batch_op.alter_column('venue_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('venue', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    with op.batch_alter_table('tables', schema=None) as batch_op:
        batch_op.alter_column('venue_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.alter_column('is_available',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', mysql.VARCHAR(length=20), nullable=True))
        batch_op.add_column(sa.Column('customer_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('order_ibfk_1', 'user', ['customer_id'], ['id'])
        batch_op.alter_column('total_price',
               existing_type=mysql.FLOAT(),
               nullable=True)
        batch_op.alter_column('venue_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
        batch_op.drop_column('created_at')
        batch_op.drop_column('user_id')

    op.create_table('table',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('number', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_available', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('venue_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], name='table_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('order_item',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('order_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('menu_item_id', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('quantity', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['menu_item_id'], ['menu_item.id'], name='order_item_ibfk_2'),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], name='order_item_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
