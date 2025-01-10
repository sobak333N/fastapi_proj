CREATE DATABASE test;

\c test

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE OR REPLACE FUNCTION hash_passwords()
RETURNS TRIGGER AS $$
BEGIN
    NEW.password_hash = crypt(NEW.password_hash, gen_salt('bf'));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER hash_passwords_trigger ON users;
CREATE TRIGGER hash_passwords_trigger
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION hash_passwords();

