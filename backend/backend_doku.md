# Plainbi Backend Documentation


## postgres repo lokal
podman run -d --name plainbi_postgres -e POSTGRES_PASSWORD=plainbi -v /home/e10002068/Projects/plainbi_home/pgdata:/var/lib/postgresql/data -p 5432:5432 postgres


PGPASSWORD=plainbi psql -h localhost -p 5432 -U postgres

Use repo docker.io/library/postgres:latest

## Environment variables

| PLAINBI_BACKEND_LOG_DEBUG | if defined run in debug mode |
| PLAINBI_BACKEND_LOGFILE   | path to the logfile, in a container this might be in a mounted volume |
| PLAINBI_BACKEND_CONFIG    | path to the configuration file. If it is not defined, a configuration logfile is searched in home directory or etc. ~/.env |
| PLAINBI_REPOSITORY        | the sqlalchemy connectstring for the repository connection. can be sqlite,mssql,postgres,oracle |
| PLAINBI_DATABASE          | an optional default database connection for the crud api. If not defined then repository plainbi_datasource with id=1 |
| PLAINBI_BACKEND_PORT      | the port for running the flask app |

## endpoints

@api.route('/', methods=['GET'])
@api.route(api_root+'/version', methods=['GET'])
@api.route(api_root+'/backend_version', methods=['GET'])
# Define routes for CRUD operations
@api.route(api_prefix+'/<tab>', methods=['GET'])
# Define routes for CRUD operations
@api.route(api_prefix+'/<tab>/<pk>', methods=['GET'])
@api.route(api_prefix+'/<tab>', methods=['POST'])
@api.route(api_prefix+'/<tab>/<pk>', methods=['PUT'])
@api.route(api_prefix+'/<tab>/<pk>', methods=['DELETE'])
@api.route(api_metadata_prefix+'/tables', methods=['GET'])
@api.route(api_metadata_prefix+'/table/<tab>', methods=['GET'])
# Define routes for CRUD operations
@api.route(repo_api_prefix+'/resources', methods=['GET'])
# Define routes for CRUD operations
@api.route(repo_api_prefix+'/<tab>', methods=['GET'])
# Define routes for CRUD operations
@api.route(repo_api_prefix+'/<tab>/<pk>', methods=['GET'])
@api.route(repo_api_prefix+'/<tab>', methods=['POST'])
@api.route(repo_api_prefix+'/<tab>/<pk>', methods=['PUT'])
@api.route(repo_api_prefix+'/<tab>/<pk>', methods=['DELETE'])
@api.route(repo_api_prefix+'/init_repo', methods=['GET'])
@api.route(repo_api_prefix+'/lookup/<id>/data', methods=['GET'])
@api.route(repo_api_prefix+'/adhoc/<id>/data', methods=['GET'])
@api.route('/login', methods=['POST'])
@api.route('/passwd', methods=['POST'])
@api.route('/hash_passwd/<pwd>', methods=['GET'])
@api.route('/cache', methods=['GET'])
@api.route('/clear_cache', methods=['GET'])
@api.route('/protected', methods=['GET'])
@api.route('/profile', methods=['GET'])
@api.route('/logout', methods=['GET'])
@api.route(api_prefix+'/crud/exec/<db>/<procedure>', methods=['POST'])

## Datasource Konfiguration

We configure the datasource for application and adhoc reports in the repository table "plainbi_datasource"

Column db_type can be

- mssql
- sqlite: then put the file nam ein "db_host"
- oracle: then use {db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
- postgres: then postgresql+psycopg2://{db_user}{db_user}:{db_pass}@{host}/{db_name}
- or any valid sqlalchemy connect string

For snowflake the sqlalchemy connect string for example is
snowflake://plainbi_dev@mmg-dwh/?warehouse=devtest_xs&database=dwh_dev&schema=PUBLIC&role=PUBLIC&authenticator=SNOWFLAKE_JWT&private_key=<a very long key>
<a very long key> is the output of 
```
def get_snowflake_private_key(pem_file_path):
    with open(pem_file_path, 'rb') as key_file:
        private_key = key_file.read()
    p_key = serialization.load_pem_private_key(private_key,password=None)
    der_key = p_key.private_bytes(encoding=serialization.Encoding.DER,format=serialization.PrivateFormat.PKCS8,encryption_algorithm=serialization.NoEncryption())
    base64_key = base64.b64encode(der_key).decode('ascii')
    base64_key = base64_key.replace('\n', '')
    while len(base64_key) % 4 != 0:
        base64_key += '='
    return  urllib.parse.quote_plus(base64_key)
```
