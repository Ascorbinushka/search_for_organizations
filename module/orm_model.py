from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import Text, VARCHAR, BOOLEAN, INT
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.types import UserDefinedType
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import relationship
from module.config import settings
from sqlalchemy.ext.declarative import declarative_base

# Создание базовой модели
Base = declarative_base()


class PolygonType(UserDefinedType):
    def get_col_spec(self):
        return "POLYGON"


class PointType(UserDefinedType):
    def get_col_spec(self):
        return "POINT"


# class BondingScansShop(Base):
#     __tablename__ = "bonding_scans_shop"
#     __table_args__ = {'schema': settings.DB_SCHEMA}
#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     shop_id: Mapped[Optional[int]] = mapped_column(INT, ForeignKey(f'{settings.DB_SCHEMA}.shops.shop_id'))
#     scan_id: Mapped[Optional[int]] = mapped_column(INT, ForeignKey(f'{settings.DB_SCHEMA}.scan_region.scan_id'))
#     distance: Mapped[Optional[float]] = mapped_column(FLOAT)


# class ScanRegion(Base):
#     __tablename__ = "scan_region"
#     __table_args__ = {'schema': settings.DB_SCHEMA}
#     scan_id: Mapped[Optional[int]] = mapped_column(primary_key=True, autoincrement=True)
#     OSM_ID: Mapped[Optional[int]] = mapped_column(INT)
#     shop = relationship("BondingScansShop")


class Shops(Base):
    __tablename__ = "shops"
    __table_args__ = {'schema': settings.DB_SCHEMA}
    shop_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    coordinate: Mapped[str] = mapped_column(PointType)
    boundery: Mapped[float] = mapped_column(PolygonType)
    address: Mapped[str] = mapped_column(Text)
    retail_id: Mapped[int] = mapped_column(INT, ForeignKey(f'{settings.DB_SCHEMA}.shop_info.retail_id'))
    work_time: Mapped[bool] = mapped_column(BOOLEAN)
    response_geocoder: Mapped[str] = mapped_column(Text)
    request_shop_id: Mapped[int] = mapped_column(INT, ForeignKey(f'{settings.DB_SCHEMA}.request_shops.request_shop_id'))
    work_mode_id: Mapped[Optional[int]] = mapped_column(INT, ForeignKey(f'{settings.DB_SCHEMA}.operating_mode.work_mode_id'))
    OSM_ID: Mapped[Optional[int]] = mapped_column(INT)


class OperatingMode(Base):
    __tablename__ = "operating_mode"
    __table_args__ = {'schema': settings.DB_SCHEMA}
    work_mode_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    info: Mapped[Optional[tuple]] = mapped_column(JSONB)
    twenty_four_hours: Mapped[Optional[bool]] = mapped_column(BOOLEAN)  # круглосуточно
    everyday: Mapped[Optional[bool]] = mapped_column(BOOLEAN)
    mon: Mapped[Optional[bool]] = mapped_column(JSONB)
    tues: Mapped[Optional[bool]] = mapped_column(JSONB)
    wed: Mapped[Optional[bool]] = mapped_column(JSONB)
    thurs: Mapped[Optional[bool]] = mapped_column(JSONB)
    fri: Mapped[Optional[bool]] = mapped_column(JSONB)
    sat: Mapped[Optional[bool]] = mapped_column(JSONB)
    sun: Mapped[Optional[bool]] = mapped_column(JSONB)
    mode = relationship("Shops")


class RequestShops(Base):
    __tablename__ = "request_shops"
    __table_args__ = {'schema': settings.DB_SCHEMA}
    request_shop_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR)
    request = relationship("Shops")


class ShopInfo(Base):
    __tablename__ = "shop_info"
    __table_args__ = {'schema': settings.DB_SCHEMA}
    retail_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(VARCHAR(200))
    name: Mapped[str] = mapped_column(VARCHAR(200))
    correctness: Mapped[Optional[int]] = mapped_column(INT)
    info = relationship("Shops")


if __name__ == "__main__":
    pass
