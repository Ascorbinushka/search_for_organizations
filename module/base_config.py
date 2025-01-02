from sqlalchemy import create_engine, Engine
from module.config import settings
from module.orm_model import Base, Shops, ShopInfo, RequestShops, OperatingMode
from sqlalchemy.orm import sessionmaker
from typing import Any


class Connector_db:
    def __init__(self, dsn: str | None = None,
                 schema: str | None = None,
                 table_key: str | None = None,
                 debug_mode: bool = False):
        self.dsn = dsn
        self.schema = schema
        self.table_key = table_key
        self.engine = self._set_engine()
        self.debug_mode = debug_mode

    def _set_engine(self) -> Engine:
        return create_engine(self.dsn, echo=self.debug_mode)


class Shops_db(Connector_db):
    def __init__(self, debug_mode: bool = False):
        self.dsn = settings.DATABASE_URL_psycopg2
        self.schema = settings.DB_SCHEMA
        self.debug_mode = debug_mode
        self.Base = Base
        super().__init__(self.dsn, self.schema, self.debug_mode)
        self.create_tables()

    def create_tables(self):
        self.Base.metadata.create_all(self.engine)

    def push_request_shops(self, name: str) -> int:
        Session = sessionmaker(bind=self.engine)
        with (Session() as session):
            request_shops = RequestShops(name=name)
            if not session.query(RequestShops).filter_by(name=name).first():
                session.add(request_shops)
            session.commit()
            get_request_shop_id = session.query(RequestShops).filter_by(name=name).first()
            session.close()
            return get_request_shop_id.request_shop_id

    def push_operating_mode(self, info: Any, twenty_four_hours: bool, everyday: bool, mon: Any, tues: Any, wed: Any,
                            thurs: Any, fri: Any, sat: Any, sun: Any) -> int:
        Session = sessionmaker(bind=self.engine)
        with (Session() as session):
            operating_mode = OperatingMode(info=info, twenty_four_hours=twenty_four_hours, everyday=everyday, mon=mon,
                                           tues=tues, wed=wed, thurs=thurs, fri=fri, sat=sat, sun=sun)
            if not session.query(OperatingMode).filter_by(info=info).first():
                session.add(operating_mode)
            session.commit()
            get_work_mode_id = session.query(OperatingMode).filter_by(info=info).first()
            session.close()
            return get_work_mode_id.work_mode_id

    def push_shop_info(self, type: str, name: str) -> int:
        session = sessionmaker(bind=self.engine)
        with (session() as session):
            shop_info = ShopInfo(type=type, name=name)
            if not session.query(ShopInfo).filter_by(name=name,
                                                     type=type).first():
                session.add(shop_info)
            session.commit()
            get_retail_id = session.query(ShopInfo).filter_by(name=name, type=type).first()
            session.close()
            return get_retail_id.retail_id

    def push_shops(self, coordinate: str, boundedBy: float | str, address: str, retail_id: int, work_time: bool,
                   response_geocoder: str,
                   request_shop_id: int, work_mode_id: int):
        session = sessionmaker(bind=self.engine)
        with (session() as session):
            shops_info = Shops(coordinate=coordinate, boundery=boundedBy, address=address, retail_id=retail_id,
                               work_time=work_time, response_geocoder=response_geocoder,
                               request_shop_id=request_shop_id,
                               work_mode_id=work_mode_id)
            if not session.query(Shops).filter_by(address=address, response_geocoder=response_geocoder).first():
                session.add(shops_info)
            session.commit()
            session.close()


if __name__ == '__main__':
    conn = Shops_db(debug_mode=False)
    print(conn)
