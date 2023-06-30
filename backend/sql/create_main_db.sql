DROP DATABASE IF EXISTS warskald_main;
CREATE DATABASE warskald_main;
USE warskald_main;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS general_data;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS battles;
DROP TABLE IF EXISTS id_registry;

CREATE TABLE users (
    username VARCHAR(256) NOT NULL PRIMARY KEY,
    email VARCHAR(256),
    passkey VARCHAR(256) NOT NULL DEFAULT ''
);

CREATE TABLE general_data (
	id VARCHAR(256) NOT NULL PRIMARY KEY,
    created_by VARCHAR(256),
	owning_user VARCHAR(256),
    last_updated_by VARCHAR(256),
    creation_date DATETIME,
    last_update_date DATETIME,
    object_type VARCHAR(256) NOT NULL DEFAULT '',
    datum_name VARCHAR(256) NOT NULL DEFAULT '',
    json_data BLOB
);

CREATE TABLE audit_logs (
	id VARCHAR(256) NOT NULL PRIMARY KEY,
    time_stamp DATETIME NOT NULL,
    data_id BIGINT NOT NULL,
    changes BLOB
);

CREATE TABLE battles (
	id VARCHAR(256) NOT NULL PRIMARY KEY,
    scheduled_date DATETIME,
    completed_date DATETIME,
    battle_status VARCHAR(256),
    users BLOB,
    rosters BLOB
    
);

CREATE TABLE id_registry (
	id VARCHAR(256) NOT NULL PRIMARY KEY
)