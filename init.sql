DO
$$ 
BEGIN 
   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mydb') THEN
      PERFORM dblink_connect('host=localhost dbname=postgres user=postgres password=postgres');
      PERFORM dblink_exec('CREATE DATABASE mydb');
   END IF;
END;
$$;
