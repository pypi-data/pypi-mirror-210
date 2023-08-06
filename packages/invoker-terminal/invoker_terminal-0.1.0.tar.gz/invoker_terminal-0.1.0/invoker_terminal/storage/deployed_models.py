from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, String, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)

from ..constants import InvokerEnvironment


class Base(DeclarativeBase):
    pass


class DeployedModel(Base):
    __tablename__ = "deployed_models"
    env: Mapped[InvokerEnvironment] = mapped_column(
        String(10), primary_key=True
    )
    model_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    image_id: Mapped[str] = mapped_column(String(71))
    model_name: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"DeployedModel(env={self.env!r}, model_id={self.model_id!r}, model_name={self.model_name!r})"


class InferenceLookup(Base):
    __tablename__ = "inference_lookup"
    env: Mapped[InvokerEnvironment] = mapped_column(
        String(10), primary_key=True
    )
    model_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    inference_id: Mapped[str] = mapped_column(BigInteger(), primary_key=True)

    def __repr__(self) -> str:
        return f"InferenceModel(env={self.env!r}, model_id={self.model_id!r}, inference_id={self.inference_id!r})"


def addDeployedModel(
    engine,
    env: InvokerEnvironment,
    model_id: int,
    image_id: str,
    model_name: int,
):
    with Session(engine) as session:
        obj = DeployedModel(
            env=env,
            model_id=model_id,
            image_id=image_id,
            model_name=model_name,
        )
        session.add(obj)
        session.commit()


def addInference(
    engine, env: InvokerEnvironment, model_id: int, inference_id: int
) -> bool:
    with Session(engine) as session:
        obj = InferenceLookup(
            env=env, model_id=model_id, inference_id=inference_id
        )
        session.add(obj)
        session.commit()
    return True


def checkInference(
    engine, env: InvokerEnvironment, model_id: int, inference_id: int
) -> bool:
    with Session(engine) as session:
        stmt = (
            select(InferenceLookup)
            .where(InferenceLookup.env == env)
            .where(InferenceLookup.model_id == model_id)
            .where(InferenceLookup.inference_id == inference_id)
        )
        inf = session.scalars(stmt).one_or_none()
        if inf:
            return True
    return False


def getDeployedModels(engine) -> list[DeployedModel]:
    with Session(engine) as session:
        stmt = select(DeployedModel)
        result = []
        for model in session.scalars(stmt):
            result.append(model)
        return result


def getImageIdByModel(engine, env: InvokerEnvironment, model_id: int) -> str:
    with Session(engine) as session:
        stmt = (
            select(DeployedModel)
            .where(DeployedModel.model_id == model_id)
            .where(DeployedModel.env == env)
        )
        model = session.scalars(stmt).one()
        return model.image_id


def updateModel(engine, model_id: int, image_id: str):
    with Session(engine) as session:
        stmt = select(DeployedModel).where(DeployedModel.model_id == model_id)
        model = session.scalars(stmt).one()
        model.image_id = image_id
        session.commit()
