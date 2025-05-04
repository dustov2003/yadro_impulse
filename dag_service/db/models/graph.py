from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from dag_service.db import DeclarativeBase

class DAG(DeclarativeBase):
    __tablename__ = "dags"
    dag_id = Column(Integer, primary_key=True)
    nodes = relationship("Node", back_populates="dag", cascade="all, delete-orphan")
    edges = relationship("Edge", back_populates="dag", cascade="all, delete-orphan")

class Node(DeclarativeBase):
    __tablename__ = "nodes"
    node_id = Column(Integer, primary_key=True)
    dag_id = Column(Integer, ForeignKey("dags.dag_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    dag = relationship("DAG", back_populates="nodes")
    __table_args__ = (
        UniqueConstraint("dag_id", "name", name="unique_dag_node_name"),
    )

class Edge(DeclarativeBase):
    __tablename__ = "edges"
    edge_id = Column(Integer, primary_key=True)
    dag_id = Column(Integer, ForeignKey("dags.dag_id", ondelete="CASCADE"), nullable=False)
    source_node_id = Column(Integer, ForeignKey("nodes.node_id", ondelete="CASCADE"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("nodes.node_id", ondelete="CASCADE"), nullable=False)
    dag = relationship("DAG", back_populates="edges")
    source_node = relationship("Node", foreign_keys=[source_node_id])
    target_node = relationship("Node", foreign_keys=[target_node_id])
    __table_args__ = (
        UniqueConstraint("dag_id", "source_node_id", "target_node_id", name="unique_dag_edge"),
        CheckConstraint("source_node_id != target_node_id", name="no_self_loops"),
    )