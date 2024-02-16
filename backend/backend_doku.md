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
