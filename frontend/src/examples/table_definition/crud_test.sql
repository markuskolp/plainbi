
DROP TABLE IF EXISTS  dwh.analysis.crud_api_testtable;
CREATE TABLE dwh.analysis.crud_api_testtable (
    nr int NOT NULL
  , name varchar(200)
  , dat date
  , PRIMARY KEY (nr)
);

DROP TABLE IF EXISTS dwh.analysis.crud_api_tv_testtable;
CREATE TABLE dwh.analysis.crud_api_tv_testtable (
    nr int NOT NULL
  , name varchar(200)
  , dat date
  , valid_from_dt datetime NOT NULL
  , invalid_from_dt datetime NOT NULL
  , last_changed_dt datetime NOT NULL
  , is_deleted char(1) NOT NULL
  , is_latest_period char(1) NOT NULL
  , is_current_and_active char(1) NOT NULL
  , last_changed_by varchar(120)
  , PRIMARY KEY (nr, invalid_from_dt)
);