from sqlalchemy import ForeignKeyConstraint as ForeignKeyConstraint_


def ForeignKeyConstraint(*args, **kwargs):
    return ForeignKeyConstraint_(
        *args,
        **kwargs,
        onupdate="CASCADE",
        ondelete="RESTRICT",
    )
