drop table if exists map_files;
create table map_files (
  id integer primary key,
  size integer not null,
  scale integer not null,
  map_obj blob,
  map_stl blob
);

drop table if exists bus_stops;
create table bus_stops (
  node_id integer,
  name text,
  ref integer
);

drop table if exists foo;
create table foo (
  id integer primary key,
  bar text
);