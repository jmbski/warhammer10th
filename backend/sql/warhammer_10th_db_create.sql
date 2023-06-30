USE warskald_main;

DROP TABLE IF EXISTS warhammer_indexes;
DROP TABLE IF EXISTS data_cards;

CREATE TABLE data_cards(
	id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    unit_name VARCHAR(256) NOT NULL DEFAULT '',
    json_data BLOB NOT NULL
);