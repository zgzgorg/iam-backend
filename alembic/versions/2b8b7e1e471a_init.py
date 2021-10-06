"""init

Revision ID: 2b8b7e1e471a
Revises: 
Create Date: 2021-10-04 17:22:33.440116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b8b7e1e471a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('account',
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('first_name', sa.String(length=30), nullable=False),
    sa.Column('last_name', sa.String(length=30), nullable=False),
    sa.Column('id', sa.String(length=100), nullable=True),
    sa.Column('chinese_name', sa.String(length=255), nullable=True),
    sa.Column('nickname', sa.String(length=255), nullable=True),
    sa.Column('phone_number', sa.String(length=30), nullable=True),
    sa.Column('shirt_size', sa.String(length=10), nullable=True),
    sa.Column('company', sa.String(length=50), nullable=True),
    sa.Column('school', sa.String(length=50), nullable=True),
    sa.Column('register_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('dietary_restriction', sa.String(length=255), nullable=True),
    sa.Column('reimbursement_platform', sa.String(length=50), nullable=True),
    sa.Column('reimbursement_method', sa.String(length=50), nullable=True),
    sa.Column('reimbursement_phone_number', sa.String(length=30), nullable=True),
    sa.Column('reimbursement_email', sa.String(length=255), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=True),
    sa.Column('birthday', sa.DateTime(), nullable=True),
    sa.Column('memo', sa.JSON(), nullable=True),
    sa.Column('type', sa.String(length=30), nullable=True),
    sa.Column('review_by_id', sa.String(length=100), nullable=True),
    sa.Column('review_status', sa.String(length=30), nullable=True),
    sa.Column('has_iam_google_account', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['review_by_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('email'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_account_email'), 'account', ['email'], unique=False)
    op.create_table('group',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('season', sa.Integer(), nullable=True),
    sa.Column('chinese_name', sa.String(length=255), nullable=True),
    sa.Column('english_name', sa.String(length=60), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('memo', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_group_email'), 'group', ['email'], unique=True)
    op.create_table('user_group',
    sa.Column('user_id', sa.String(length=100), nullable=False),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_group')
    op.drop_index(op.f('ix_group_email'), table_name='group')
    op.drop_table('group')
    op.drop_index(op.f('ix_account_email'), table_name='account')
    op.drop_table('account')
    # ### end Alembic commands ###