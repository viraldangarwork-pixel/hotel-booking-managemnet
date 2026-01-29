"""Add guest document image fields

Revision ID: 002_guest_docs
Revises: 001_initial
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_guest_docs'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('guests', sa.Column('id_document_front_url', sa.String(500), nullable=True))
    op.add_column('guests', sa.Column('id_document_back_url', sa.String(500), nullable=True))
    op.add_column('guests', sa.Column('document_clarity_status', sa.String(20), nullable=True))
    op.add_column('guests', sa.Column('document_clarity_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('guests', 'document_clarity_notes')
    op.drop_column('guests', 'document_clarity_status')
    op.drop_column('guests', 'id_document_back_url')
    op.drop_column('guests', 'id_document_front_url')
