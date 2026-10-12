CREATE DATABASE IF NOT EXISTS icd10_langchain;
USE icd10_langchain;

CREATE TABLE IF NOT EXISTS icd10_codes (
    code VARCHAR(10) PRIMARY KEY,
    description VARCHAR(500) NOT NULL,
    FULLTEXT KEY ft_description (description)
);