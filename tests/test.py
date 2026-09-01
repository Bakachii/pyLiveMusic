from pyLiveMusic import pyLiveMusic, MongoDB

DB_URL = "mongodb+srv://dokib34191_db_user:WdJVTNTbqZJfgDf7@cluster0.p4wdks9.mongodb.net/?appName=Cluster0"

server = pyLiveMusic(AUTH_KEY="124", STORAGE=MongoDB(db_url=DB_URL))

server.start() 