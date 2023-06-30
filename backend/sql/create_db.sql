#    KEY `FK_audit_user` (user),
#    CONSTRAINT `FK_audit_data` FOREIGN KEY (object_id) REFERENCES data_objects (object_id) ON DELETE CASCADE ON UPDATE CASCADE,
USE warskald_primary;

DROP TABLE IF EXISTS data_models;
DROP TABLE IF EXISTS data_types;
DROP TABLE IF EXISTS data_properties;
DROP TABLE IF EXISTS data_instances;
DROP TABLE IF EXISTS instance_properties;
DROP TABLE IF EXISTS model_properties;
DROP TABLE IF EXISTS audit_log;

CREATE TABLE audit_log (
	id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user VARCHAR(255) NOT NULL,
    action VARCHAR(255),
    changes BLOB NOT NULL,
    audit_date TIMESTAMP,
    KEY `FK_audit_user` (user),
    CONSTRAINT `FK_audit_x_users` FOREIGN KEY (user) REFERENCES users (userName) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_models (
	id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    datum_name VARCHAR(255) NOT NULL,
    created_by VARCHAR(255) NOT NULL,
    KEY `FK_user` (created_by),
    CONSTRAINT `FK_models_user` FOREIGN KEY (created_by) REFERENCES users (userName) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_types(
	id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    datum_name VARCHAR(255) NOT NULL,
    definition BIGINT NOT NULL,
    default_value BLOB,
    KEY `FK_model_definition` (definition),
    CONSTRAINT `FK_types_models` FOREIGN KEY (definition) REFERENCES data_models (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_instances (
	id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    datum_name VARCHAR(255) NOT NULL,
    model_id BIGINT NOT NULL,
    KEY `FK_model_id` (model_id),
    CONSTRAINT `FK_instances_models` FOREIGN KEY(model_id) REFERENCES data_models (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE data_properties (
	id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    datum_name VARCHAR(255) NOT NULL,
    type_id BIGINT NOT NULL,
    default_value BLOB,
    current_value BLOB,
    KEY `FK_type_id` (type_id),
    CONSTRAINT `FK_props_types` FOREIGN KEY (type_id) REFERENCES data_types (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE instance_properties (
	id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    instance_id BIGINT NOT NULL,
    property_id BIGINT NOT NULL,
    KEY `FK_instance_id` (instance_id),
    KEY `FK_property_id` (property_id),
    CONSTRAINT `FK_ixp_instances` FOREIGN KEY (instance_id) REFERENCES data_instances (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_ixp_props` FOREIGN KEY (property_id) REFERENCES data_properties (id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE model_properties (
	id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
    model_id BIGINT NOT NULL,
    property_id BIGINT NOT NULL,
    KEY `FK_model_id` (model_id),
    KEY `FK_property_id` (property_id),
    CONSTRAINT `FK_ixp_models` FOREIGN KEY (model_id) REFERENCES data_models (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `FK_ixp_props` FOREIGN KEY (property_id) REFERENCES data_properties (id) ON DELETE CASCADE ON UPDATE CASCADE
);

#INSERT INTO data_models (datum_name, created_by) VALUES ('Number', 'warskald');
#INSERT INTO 