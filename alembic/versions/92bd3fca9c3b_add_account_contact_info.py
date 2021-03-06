"""add_account_contact_info

Revision ID: 92bd3fca9c3b
Revises: 3f5ad8caef2b
Create Date: 2021-10-25 21:11:14.798881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "92bd3fca9c3b"
down_revision = "3f5ad8caef2b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("account", schema=None) as batch_op:
        batch_op.add_column(sa.Column("wechat_id", sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column("line_id", sa.String(length=30), nullable=True))
        batch_op.alter_column("phone_number", existing_type=sa.VARCHAR(length=30), nullable=False)

    with op.batch_alter_table("account_token", schema=None) as batch_op:
        batch_op.alter_column("account_id", existing_type=sa.VARCHAR(length=100), nullable=True)
        batch_op.alter_column("token", existing_type=sa.VARCHAR(length=300), nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("account_token", schema=None) as batch_op:
        batch_op.alter_column("token", existing_type=sa.VARCHAR(length=300), nullable=True)
        batch_op.alter_column("account_id", existing_type=sa.VARCHAR(length=100), nullable=False)

    with op.batch_alter_table("account", schema=None) as batch_op:
        batch_op.alter_column("phone_number", existing_type=sa.VARCHAR(length=30), nullable=True)
        batch_op.drop_column("line_id")
        batch_op.drop_column("wechat_id")

    # ### end Alembic commands ###
