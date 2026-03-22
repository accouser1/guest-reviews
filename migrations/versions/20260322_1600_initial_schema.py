"""initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-22 16:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create hotels table
    op.create_table(
        'hotels',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('legal_name', sa.String(255), nullable=False),
        sa.Column('address', postgresql.JSON, nullable=False),
        sa.Column('phone', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('super_admin', 'owner', 'manager', 'auditor', name='userrole'), nullable=False),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_hotel_id', 'users', ['hotel_id'])
    
    # Create hotel_branches table
    op.create_table(
        'hotel_branches',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', postgresql.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_hotel_branches_hotel_id', 'hotel_branches', ['hotel_id'])
    
    # Create hotel_settings table
    op.create_table(
        'hotel_settings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('deposit_policy', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('risk_thresholds', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('auto_scoring_enabled', sa.Boolean, default=True, nullable=False),
        sa.Column('notification_preferences', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('custom_risk_rules', postgresql.JSON, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_hotel_settings_hotel_id', 'hotel_settings', ['hotel_id'])
    
    # Create integrations table
    op.create_table(
        'integrations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(100), nullable=False),
        sa.Column('credentials', postgresql.JSON, nullable=False),
        sa.Column('webhook_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean, default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_integrations_hotel_id', 'integrations', ['hotel_id'])
    
    # Create guests table
    op.create_table(
        'guests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('birth_date', sa.Date, nullable=True),
        sa.Column('document_number', sa.String(100), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('risk_level', sa.Enum('low', 'medium', 'high', 'critical', name='risklevel'), default='medium', nullable=False),
        sa.Column('blacklist_flag', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_guests_first_name', 'guests', ['first_name'])
    op.create_index('ix_guests_last_name', 'guests', ['last_name'])
    op.create_index('ix_guests_phone', 'guests', ['phone'])
    op.create_index('ix_guests_email', 'guests', ['email'])
    op.create_index('ix_guests_document_number', 'guests', ['document_number'])
    op.create_index('ix_guests_risk_level', 'guests', ['risk_level'])
    op.create_index('ix_guests_blacklist_flag', 'guests', ['blacklist_flag'])
    
    # Create risk_scores table
    op.create_table(
        'risk_scores',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('guest_id', sa.String(36), sa.ForeignKey('guests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('booking_id', sa.String(36), nullable=True),
        sa.Column('score', sa.Integer, nullable=False),
        sa.Column('risk_level', sa.String(20), nullable=False),
        sa.Column('reasons', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('recommendation', sa.Text, nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_risk_scores_guest_id', 'risk_scores', ['guest_id'])
    op.create_index('ix_risk_scores_hotel_id', 'risk_scores', ['hotel_id'])
    op.create_index('ix_risk_scores_booking_id', 'risk_scores', ['booking_id'])
    op.create_index('ix_risk_scores_calculated_at', 'risk_scores', ['calculated_at'])
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('branch_id', sa.String(36), sa.ForeignKey('hotel_branches.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source', sa.String(100), nullable=False),
        sa.Column('booking_external_id', sa.String(255), nullable=False),
        sa.Column('guest_id', sa.String(36), sa.ForeignKey('guests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('checkin_date', sa.Date, nullable=False),
        sa.Column('checkout_date', sa.Date, nullable=False),
        sa.Column('room_type', sa.String(100), nullable=False),
        sa.Column('room_number', sa.String(50), nullable=True),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='RUB'),
        sa.Column('status', sa.Enum('new', 'pending_check', 'checked', 'approved', 'approved_with_deposit', 'rejected', 'checked_in', 'checked_out', 'cancelled', name='bookingstatus'), default='new', nullable=False),
        sa.Column('risk_score_id', sa.String(36), sa.ForeignKey('risk_scores.id', ondelete='SET NULL'), nullable=True),
        sa.Column('deposit_id', sa.String(36), nullable=True),
        sa.Column('notes', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_bookings_hotel_id', 'bookings', ['hotel_id'])
    op.create_index('ix_bookings_branch_id', 'bookings', ['branch_id'])
    op.create_index('ix_bookings_guest_id', 'bookings', ['guest_id'])
    op.create_index('ix_bookings_booking_external_id', 'bookings', ['booking_external_id'])
    op.create_index('ix_bookings_checkin_date', 'bookings', ['checkin_date'])
    op.create_index('ix_bookings_checkout_date', 'bookings', ['checkout_date'])
    op.create_index('ix_bookings_status', 'bookings', ['status'])
    
    # Create deposits table
    op.create_table(
        'deposits',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='RUB'),
        sa.Column('status', sa.Enum('not_required', 'required', 'hold_pending', 'held', 'partially_charged', 'charged', 'released', 'failed', name='depositstatus'), default='required', nullable=False),
        sa.Column('payment_provider_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_deposits_booking_id', 'deposits', ['booking_id'])
    op.create_index('ix_deposits_status', 'deposits', ['status'])
    
    # Add foreign key for bookings.deposit_id
    op.create_foreign_key('fk_bookings_deposit_id', 'bookings', 'deposits', ['deposit_id'], ['id'], ondelete='SET NULL')
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('deposit_id', sa.String(36), sa.ForeignKey('deposits.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.Enum('hold', 'charge', 'release', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', name='transactionstatus'), default='pending', nullable=False),
        sa.Column('provider_transaction_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_transactions_deposit_id', 'transactions', ['deposit_id'])
    op.create_index('ix_transactions_status', 'transactions', ['status'])
    
    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('booking_id', sa.String(36), sa.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('guest_id', sa.String(36), sa.ForeignKey('guests.id', ondelete='CASCADE'), nullable=False),
        sa.Column('hotel_id', sa.String(36), sa.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('author_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('damage_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('unpaid_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('evidence_files', postgresql.ARRAY(sa.String), nullable=False, server_default='{}'),
        sa.Column('moderation_status', sa.Enum('pending', 'approved', 'hidden', 'disputed', name='moderationstatus'), default='approved', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_reviews_booking_id', 'reviews', ['booking_id'])
    op.create_index('ix_reviews_guest_id', 'reviews', ['guest_id'])
    op.create_index('ix_reviews_hotel_id', 'reviews', ['hotel_id'])
    op.create_index('ix_reviews_author_id', 'reviews', ['author_id'])
    op.create_index('ix_reviews_moderation_status', 'reviews', ['moderation_status'])
    
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('data', postgresql.JSON, nullable=True),
        sa.Column('is_read', sa.Boolean, default=False, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])
    op.create_index('ix_notifications_type', 'notifications', ['type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('reviews')
    op.drop_table('transactions')
    op.drop_table('deposits')
    op.drop_table('bookings')
    op.drop_table('risk_scores')
    op.drop_table('guests')
    op.drop_table('integrations')
    op.drop_table('hotel_settings')
    op.drop_table('hotel_branches')
    op.drop_table('users')
    op.drop_table('hotels')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS userrole')
    op.execute('DROP TYPE IF EXISTS risklevel')
    op.execute('DROP TYPE IF EXISTS bookingstatus')
    op.execute('DROP TYPE IF EXISTS depositstatus')
    op.execute('DROP TYPE IF EXISTS transactiontype')
    op.execute('DROP TYPE IF EXISTS transactionstatus')
    op.execute('DROP TYPE IF EXISTS moderationstatus')
