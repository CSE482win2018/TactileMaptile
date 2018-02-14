drop table if exists map_files;
create table map_files (
  id integer primary key,
  map_obj blob not null
);

drop table if exists foo;
create table foo (
  id integer primary key,
  bar text
);