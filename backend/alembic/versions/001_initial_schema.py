"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema."""
    
    # RCA Sessions table
    op.create_table(
        'rca_sessions',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('lot_id', sa.String(length=255), nullable=False),
        sa.Column('wafer_id', sa.String(length=255), nullable=True),
        sa.Column('bin', sa.Integer(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress_percentage', sa.Integer(), nullable=True),
        sa.Column('wafer_map_path', sa.String(length=500), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rca_sessions_lot_id', 'rca_sessions', ['lot_id'])
    op.create_index('ix_rca_sessions_status', 'rca_sessions', ['status'])
    op.create_index('ix_rca_sessions_user_id', 'rca_sessions', ['user_id'])
    
    # Agents table
    op.create_table(
        'agents',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rca_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agents_session_id', 'agents', ['session_id'])
    
    # Agent Messages table
    op.create_table(
        'agent_messages',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('sender_agent', sa.String(length=255), nullable=False),
        sa.Column('recipient_agent', sa.String(length=255), nullable=True),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rca_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_agent_messages_session_id', 'agent_messages', ['session_id'])
    
    # Hypotheses table
    op.create_table(
        'hypotheses',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('rank', sa.Integer(), nullable=False),
        sa.Column('hypothesis_text', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rca_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_hypotheses_session_id', 'hypotheses', ['session_id'])
    
    # RCA Reports table
    op.create_table(
        'rca_reports',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('report_path', sa.String(length=500), nullable=False),
        sa.Column('format', sa.String(length=50), nullable=False),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rca_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rca_reports_session_id', 'rca_reports', ['session_id'])
    
    # User Feedback table
    op.create_table(
        'user_feedback',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('hypothesis_id', sa.String(length=255), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rca_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_feedback_session_id', 'user_feedback', ['session_id'])
    
    # Tool Executions table
    op.create_table(
        'tool_executions',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('agent_id', sa.String(length=255), nullable=False),
        sa.Column('tool_name', sa.String(length=255), nullable=False),
        sa.Column('input_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tool_executions_agent_id', 'tool_executions', ['agent_id'])
    
    # STDF Data Cache table
    op.create_table(
        'stdf_data_cache',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('lot_id', sa.String(length=255), nullable=False),
        sa.Column('wafer_id', sa.String(length=255), nullable=True),
        sa.Column('s3_path', sa.String(length=500), nullable=False),
        sa.Column('parsed_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('cached_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_stdf_data_cache_lot_wafer', 'stdf_data_cache', ['lot_id', 'wafer_id'])
    
    # Wafer Maps table
    op.create_table(
        'wafer_maps',
        sa.Column('id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('s3_path', sa.String(length=500), nullable=False),
        sa.Column('bin', sa.Integer(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rca_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_wafer_maps_session_id', 'wafer_maps', ['session_id'])


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('ix_wafer_maps_session_id', table_name='wafer_maps')
    op.drop_table('wafer_maps')
    
    op.drop_index('ix_stdf_data_cache_lot_wafer', table_name='stdf_data_cache')
    op.drop_table('stdf_data_cache')
    
    op.drop_index('ix_tool_executions_agent_id', table_name='tool_executions')
    op.drop_table('tool_executions')
    
    op.drop_index('ix_user_feedback_session_id', table_name='user_feedback')
    op.drop_table('user_feedback')
    
    op.drop_index('ix_rca_reports_session_id', table_name='rca_reports')
    op.drop_table('rca_reports')
    
    op.drop_index('ix_hypotheses_session_id', table_name='hypotheses')
    op.drop_table('hypotheses')
    
    op.drop_index('ix_agent_messages_session_id', table_name='agent_messages')
    op.drop_table('agent_messages')
    
    op.drop_index('ix_agents_session_id', table_name='agents')
    op.drop_table('agents')
    
    op.drop_index('ix_rca_sessions_user_id', table_name='rca_sessions')
    op.drop_index('ix_rca_sessions_status', table_name='rca_sessions')
    op.drop_index('ix_rca_sessions_lot_id', table_name='rca_sessions')
    op.drop_table('rca_sessions')
