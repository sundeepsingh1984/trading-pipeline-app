"""empty message

Revision ID: 124fb039a587
Revises: 
Create Date: 2021-09-13 22:18:34.633905

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '124fb039a587'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('source',
    sa.Column('source_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('source_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('source_id')
    )
    op.create_index(op.f('ix_source_source_id'), 'source', ['source_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('source_data',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('data_type', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['source_id'], ['source.source_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_source_data_id'), 'source_data', ['id'], unique=False)
    op.create_table('user_strategies',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('strategy_name', sa.String(), nullable=False),
    sa.Column('backtested', sa.Boolean(), nullable=True),
    sa.Column('backtest_id', postgresql.ARRAY(sa.Integer()), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_strategies_id'), 'user_strategies', ['id'], unique=False)
    op.create_table('backtests',
    sa.Column('backtest_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('strategy_id', sa.Integer(), nullable=True),
    sa.Column('avg_return_mon', sa.Float(), nullable=True),
    sa.Column('sd_monthly', sa.Float(), nullable=True),
    sa.Column('avg_return_annual', sa.Float(), nullable=True),
    sa.Column('avg_std', sa.Float(), nullable=True),
    sa.Column('sharpe_ratio', sa.Float(), nullable=True),
    sa.Column('colmar_ratio', sa.Float(), nullable=True),
    sa.Column('worst_monthly_drw_dwn', sa.Float(), nullable=True),
    sa.Column('best_month_performance', sa.Float(), nullable=True),
    sa.Column('worst_drw_down', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['strategy_id'], ['user_strategies.id'], ),
    sa.PrimaryKeyConstraint('backtest_id')
    )
    op.create_index(op.f('ix_backtests_backtest_id'), 'backtests', ['backtest_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_backtests_backtest_id'), table_name='backtests')
    op.drop_table('backtests')
    op.drop_index(op.f('ix_user_strategies_id'), table_name='user_strategies')
    op.drop_table('user_strategies')
    op.drop_index(op.f('ix_source_data_id'), table_name='source_data')
    op.drop_table('source_data')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_source_source_id'), table_name='source')
    op.drop_table('source')
    # ### end Alembic commands ###
