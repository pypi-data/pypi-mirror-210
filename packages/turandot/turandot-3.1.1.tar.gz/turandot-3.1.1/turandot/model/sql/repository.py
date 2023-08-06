from pathlib import Path
from sqlalchemy import select, update, delete
from sqlalchemy.exc import NoResultFound

from turandot.model import ConfigModel
from turandot.model.sql import DbEngine, DbCsl, DbTemplate, DbFileSelectPersistence


class Repository:

    def __init__(self):
        self.engine = DbEngine()
        self.config = ConfigModel()

    def use_test_db(self, echo=False):
        self.engine.use_test_db(echo=echo)

    def get_csl(self, dbid: int) -> dict | None:
        try:
            with self.engine.create_session() as session:
                stmt = select(DbCsl).where(DbCsl.dbid == dbid)
                row = session.scalars(stmt).one()
            return {"path": Path(row.path), "dbid": row.dbid}
        except NoResultFound:
            return None

    def get_all_csl(self) -> list[dict]:
        with self.engine.create_session() as session:
            stmt = select(DbCsl)
            reslist = []
            for i in session.scalars(stmt):
                reslist.append({"path": Path(i.path), "dbid": i.dbid})
        return reslist

    def save_csl(self, dbid: int | None, path: Path) -> int:
        with self.engine.create_session() as session:
            if dbid is None:
                dbmodel = DbCsl(path=str(path))
                session.add(dbmodel)
                session.commit()
                return dbmodel.dbid
            else:
                stmt = update(DbCsl).where(DbCsl.dbid == dbid).values(path=str(Path))
                session.execute(stmt)
                session.commit()
                return dbid

    def delete_csl(self, dbid) -> None:
        with self.engine.create_session() as session:
            stmt = delete(DbCsl).where(DbCsl.dbid == dbid)
            session.execute(stmt)
            session.commit()

    def get_template(self, dbid: int) -> dict | None:
        try:
            with self.engine.create_session() as session:
                stmt = select(DbTemplate).where(DbTemplate.dbid == dbid)
                row = session.scalars(stmt).one()
            return {
                "path": Path(row.path),
                "dbid": row.dbid,
                "allow_jinja": row.allow_jinja,
                "allow_mako": row.allow_mako
            }
        except NoResultFound:
            return None

    def get_all_templates(self) -> list[dict]:
        with self.engine.create_session() as session:
            stmt = select(DbTemplate)
            reslist = []
            for i in session.scalars(stmt):
                reslist.append({
                    "path": Path(i.path),
                    "dbid": i.dbid,
                    "allow_jinja": i.allow_jinja,
                    "allow_mako": i.allow_mako
                })
        return reslist

    def save_template(self, dbid: int | None, path: Path, allow_jinja: bool, allow_mako: bool) -> int:
        with self.engine.create_session() as session:
            if dbid is None:
                dbmodel = DbTemplate(
                    path=str(path),
                    allow_jinja=allow_jinja,
                    allow_mako=allow_mako
                )
                session.add(dbmodel)
                session.commit()
                return dbmodel.dbid
            else:
                stmt = update(DbTemplate).where(DbTemplate.dbid == dbid).values(
                    path=str(path),
                    allow_jinja=allow_jinja,
                    allow_mako=allow_mako
                )
                session.execute(stmt)
                session.commit()
                return dbid

    def delete_template(self, dbid) -> None:
        with self.engine.create_session() as session:
            stmt = delete(DbTemplate).where(DbTemplate.dbid == dbid)
            session.execute(stmt)
            session.commit()

    def get_file_select_persist(self, selector_id: str) -> Path:
        try:
            with self.engine.create_session() as session:
                stmt = select(DbFileSelectPersistence).where(DbFileSelectPersistence.input_id == selector_id)
                row = session.scalars(stmt).one()
            return Path(row.last_path)
        except NoResultFound:
            return Path.home()

    def set_file_select_persist(self, selector_id: str, path: Path):
        with self.engine.create_session() as session:
            dbmodel = DbFileSelectPersistence(input_id=selector_id, last_path=str(path))
            session.merge(dbmodel)
            session.commit()
