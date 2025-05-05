"""empty message

Revision ID: 2c32dbfad6ef
Revises:
Create Date: 2025-05-04 17:10:34.003411

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2c32dbfad6ef"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dags", sa.Column("dag_id", sa.Integer, primary_key=True, autoincrement=True)
    )

    op.create_table(
        "nodes",
        sa.Column("node_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "dag_id",
            sa.Integer,
            sa.ForeignKey("dags.dag_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.UniqueConstraint("dag_id", "name", name="unique_dag_node_name"),
    )

    op.create_table(
        "edges",
        sa.Column("edge_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "dag_id",
            sa.Integer,
            sa.ForeignKey("dags.dag_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source_node_id",
            sa.Integer,
            sa.ForeignKey("nodes.node_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "target_node_id",
            sa.Integer,
            sa.ForeignKey("nodes.node_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "dag_id", "source_node_id", "target_node_id", name="unique_dag_edge"
        ),
        sa.CheckConstraint("source_node_id != target_node_id", name="no_self_loops"),
    )


def downgrade() -> None:
    op.drop_table("edges")
    op.drop_table("nodes")
    op.drop_table("dags")
