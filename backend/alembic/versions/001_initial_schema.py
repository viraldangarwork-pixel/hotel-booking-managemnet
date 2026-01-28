"""Initial database schema

Revision ID: 001_initial
Revises:
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Hotels table
    op.create_table(
        'hotels',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=False),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('total_floors', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('total_rooms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('amenities', sa.JSON(), nullable=True),
        sa.Column('check_in_time', sa.String(10), nullable=False, server_default='14:00'),
        sa.Column('check_out_time', sa.String(10), nullable=False, server_default='11:00'),
        sa.Column('tax_rate', sa.Integer(), server_default='18'),
        sa.Column('gst_number', sa.String(50), nullable=True),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('primary_color', sa.String(7), server_default='#2563eb'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_hotels_id'), 'hotels', ['id'])

    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('role', sa.Enum('superadmin', 'admin', 'manager', 'receptionist', 'staff', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Room types table
    op.create_table(
        'room_types',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_price', sa.Numeric(10, 2), nullable=False),
        sa.Column('extra_bed_price', sa.Numeric(10, 2), server_default='0'),
        sa.Column('max_occupancy', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('max_adults', sa.Integer(), nullable=False, server_default='2'),
        sa.Column('max_children', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('bed_type', sa.String(50), nullable=True),
        sa.Column('room_size', sa.Integer(), nullable=True),
        sa.Column('amenities', sa.JSON(), nullable=True),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_room_types_id'), 'room_types', ['id'])

    # Rooms table
    op.create_table(
        'rooms',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('room_type_id', sa.Integer(), sa.ForeignKey('room_types.id'), nullable=False),
        sa.Column('room_number', sa.String(20), nullable=False),
        sa.Column('floor', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.Enum('available', 'booked', 'checked_in', 'checked_out', 'maintenance', 'cleaning', name='roomstatus'), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('custom_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'])

    # Guests table
    op.create_table(
        'guests',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('whatsapp_number', sa.String(20), nullable=True),
        sa.Column('id_type', sa.String(50), nullable=True),
        sa.Column('id_number', sa.String(100), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('is_vip', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_blacklisted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('preferences', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('total_stays', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_spent', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_visit', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_guests_id'), 'guests', ['id'])
    op.create_index(op.f('ix_guests_email'), 'guests', ['email'])
    op.create_index(op.f('ix_guests_phone'), 'guests', ['phone'])
    op.create_index(op.f('ix_guests_whatsapp_number'), 'guests', ['whatsapp_number'])

    # Bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('booking_ref', sa.String(20), nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('room_id', sa.Integer(), sa.ForeignKey('rooms.id'), nullable=False),
        sa.Column('guest_id', sa.Integer(), sa.ForeignKey('guests.id'), nullable=False),
        sa.Column('check_in_date', sa.Date(), nullable=False),
        sa.Column('check_out_date', sa.Date(), nullable=False),
        sa.Column('actual_check_in', sa.DateTime(), nullable=True),
        sa.Column('actual_check_out', sa.DateTime(), nullable=True),
        sa.Column('adults', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('children', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('extra_beds', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.Enum('inquiry', 'pending', 'confirmed', 'checked_in', 'checked_out', 'cancelled', 'no_show', name='bookingstatus'), nullable=False),
        sa.Column('source', sa.Enum('direct', 'website', 'whatsapp', 'phone', 'walk_in', 'ota', 'corporate', name='bookingsource'), nullable=False),
        sa.Column('room_rate', sa.Numeric(10, 2), nullable=False),
        sa.Column('extra_bed_charge', sa.Numeric(10, 2), server_default='0'),
        sa.Column('subtotal', sa.Numeric(10, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(10, 2), server_default='0'),
        sa.Column('discount_amount', sa.Numeric(10, 2), server_default='0'),
        sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('discount_code', sa.String(50), nullable=True),
        sa.Column('discount_percent', sa.Integer(), server_default='0'),
        sa.Column('amount_paid', sa.Numeric(10, 2), server_default='0'),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('special_requests', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('additional_charges', sa.JSON(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'])
    op.create_index(op.f('ix_bookings_booking_ref'), 'bookings', ['booking_ref'], unique=True)

    # Payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('booking_id', sa.Integer(), sa.ForeignKey('bookings.id'), nullable=False),
        sa.Column('amount', sa.Numeric(10, 2), nullable=False),
        sa.Column('payment_method', sa.String(50), nullable=False),
        sa.Column('status', sa.Enum('pending', 'completed', 'failed', 'refunded', name='paymentstatus'), nullable=False),
        sa.Column('transaction_id', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'])

    # WhatsApp chats table
    op.create_table(
        'whatsapp_chats',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('guest_id', sa.Integer(), sa.ForeignKey('guests.id'), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_whatsapp_chats_id'), 'whatsapp_chats', ['id'])

    # WhatsApp messages table
    op.create_table(
        'whatsapp_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chat_id', sa.Integer(), sa.ForeignKey('whatsapp_chats.id'), nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),
        sa.Column('message_type', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('media_url', sa.String(500), nullable=True),
        sa.Column('wa_message_id', sa.String(100), nullable=True),
        sa.Column('status', sa.String(20), server_default='sent'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_whatsapp_messages_id'), 'whatsapp_messages', ['id'])

    # AI chat sessions table
    op.create_table(
        'ai_chat_sessions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('guest_id', sa.Integer(), sa.ForeignKey('guests.id'), nullable=True),
        sa.Column('session_type', sa.String(20), nullable=False),
        sa.Column('context', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ai_chat_sessions_id'), 'ai_chat_sessions', ['id'])

    # AI chat messages table
    op.create_table(
        'ai_chat_messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), sa.ForeignKey('ai_chat_sessions.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(50), nullable=True),
        sa.Column('confidence', sa.Numeric(3, 2), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_ai_chat_messages_id'), 'ai_chat_messages', ['id'])

    # Theme settings table
    op.create_table(
        'theme_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('primary_color', sa.String(7), server_default='#2563eb'),
        sa.Column('secondary_color', sa.String(7), server_default='#64748b'),
        sa.Column('accent_color', sa.String(7), server_default='#f59e0b'),
        sa.Column('success_color', sa.String(7), server_default='#10b981'),
        sa.Column('warning_color', sa.String(7), server_default='#f59e0b'),
        sa.Column('error_color', sa.String(7), server_default='#ef4444'),
        sa.Column('background_color', sa.String(7), server_default='#ffffff'),
        sa.Column('surface_color', sa.String(7), server_default='#f8fafc'),
        sa.Column('card_color', sa.String(7), server_default='#ffffff'),
        sa.Column('text_primary', sa.String(7), server_default='#1e293b'),
        sa.Column('text_secondary', sa.String(7), server_default='#64748b'),
        sa.Column('dark_background', sa.String(7), server_default='#0f172a'),
        sa.Column('dark_surface', sa.String(7), server_default='#1e293b'),
        sa.Column('dark_card', sa.String(7), server_default='#334155'),
        sa.Column('dark_text_primary', sa.String(7), server_default='#f8fafc'),
        sa.Column('dark_text_secondary', sa.String(7), server_default='#94a3b8'),
        sa.Column('font_family', sa.String(100), server_default='Inter, sans-serif'),
        sa.Column('font_size_base', sa.String(10), server_default='16px'),
        sa.Column('font_weight_normal', sa.String(10), server_default='400'),
        sa.Column('font_weight_medium', sa.String(10), server_default='500'),
        sa.Column('font_weight_bold', sa.String(10), server_default='700'),
        sa.Column('border_radius_sm', sa.String(10), server_default='4px'),
        sa.Column('border_radius_md', sa.String(10), server_default='8px'),
        sa.Column('border_radius_lg', sa.String(10), server_default='12px'),
        sa.Column('border_radius_xl', sa.String(10), server_default='16px'),
        sa.Column('spacing_unit', sa.String(10), server_default='4px'),
        sa.Column('shadow_sm', sa.String(100)),
        sa.Column('shadow_md', sa.String(100)),
        sa.Column('shadow_lg', sa.String(100)),
        sa.Column('logo_url', sa.String(500), nullable=True),
        sa.Column('logo_dark_url', sa.String(500), nullable=True),
        sa.Column('favicon_url', sa.String(500), nullable=True),
        sa.Column('brand_name', sa.String(255), nullable=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hotel_id'),
    )
    op.create_index(op.f('ix_theme_settings_id'), 'theme_settings', ['id'])

    # Hotel settings table
    op.create_table(
        'hotel_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('hotel_id', sa.Integer(), sa.ForeignKey('hotels.id'), nullable=False),
        sa.Column('allow_same_day_booking', sa.Boolean(), server_default='true'),
        sa.Column('min_advance_booking_days', sa.Integer(), server_default='0'),
        sa.Column('max_advance_booking_days', sa.Integer(), server_default='365'),
        sa.Column('booking_confirmation_required', sa.Boolean(), server_default='false'),
        sa.Column('free_cancellation_hours', sa.Integer(), server_default='24'),
        sa.Column('cancellation_fee_percent', sa.Integer(), server_default='0'),
        sa.Column('early_check_in_charge', sa.Integer(), server_default='0'),
        sa.Column('late_check_out_charge', sa.Integer(), server_default='0'),
        sa.Column('require_advance_payment', sa.Boolean(), server_default='false'),
        sa.Column('advance_payment_percent', sa.Integer(), server_default='0'),
        sa.Column('accepted_payment_methods', sa.JSON(), nullable=True),
        sa.Column('send_booking_confirmation_email', sa.Boolean(), server_default='true'),
        sa.Column('send_booking_confirmation_whatsapp', sa.Boolean(), server_default='true'),
        sa.Column('send_check_in_reminder', sa.Boolean(), server_default='true'),
        sa.Column('reminder_hours_before', sa.Integer(), server_default='24'),
        sa.Column('whatsapp_bot_enabled', sa.Boolean(), server_default='true'),
        sa.Column('whatsapp_bot_languages', sa.JSON(), nullable=True),
        sa.Column('whatsapp_auto_reply_enabled', sa.Boolean(), server_default='true'),
        sa.Column('whatsapp_working_hours', sa.JSON(), nullable=True),
        sa.Column('ai_assistant_enabled', sa.Boolean(), server_default='true'),
        sa.Column('ai_auto_suggestions', sa.Boolean(), server_default='true'),
        sa.Column('seasonal_pricing', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hotel_id'),
    )
    op.create_index(op.f('ix_hotel_settings_id'), 'hotel_settings', ['id'])


def downgrade() -> None:
    op.drop_table('hotel_settings')
    op.drop_table('theme_settings')
    op.drop_table('ai_chat_messages')
    op.drop_table('ai_chat_sessions')
    op.drop_table('whatsapp_messages')
    op.drop_table('whatsapp_chats')
    op.drop_table('payments')
    op.drop_table('bookings')
    op.drop_table('guests')
    op.drop_table('rooms')
    op.drop_table('room_types')
    op.drop_table('users')
    op.drop_table('hotels')

    # Drop enum types
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='roomstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='bookingstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='bookingsource').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='paymentstatus').drop(op.get_bind(), checkfirst=True)
