"""add user followers_count

Revision ID: f7afcb8f4842
Revises: b4a55cc3dbae
Create Date: 2026-02-19 16:10:01.547598
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f7afcb8f4842'
down_revision: Union[str, Sequence[str], None] = 'b4a55cc3dbae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. Добавляем nullable колонки (без default пока)
    op.add_column('users', sa.Column('followers_count', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('following_count', sa.Integer(), nullable=True))

    # 2. Заполняем 0 для всех существующих пользователей
    op.execute("UPDATE users SET followers_count = 0")
    op.execute("UPDATE users SET following_count = 0")

    # 3. Теперь делаем NOT NULL
    op.alter_column('users', 'followers_count', nullable=False)
    op.alter_column('users', 'following_count', nullable=False)

def downgrade() -> None:
    op.drop_column('users', 'following_count')
    op.drop_column('users', 'followers_count')
