import os

from spt_factory import MongoFactory


if __name__ == '__main__':
    print(os.getenv('SSLROOT'))
    f = MongoFactory(
        mongo_url=os.getenv('MONGO_URL'),
        tlsCAFile=os.getenv('SSLROOT'),
    )

    print(f.get_greenplum_credentials())
    with f.get_greenplum() as conn:
        with conn.cursor() as cur:
            cur.execute('select * from test.raw_data')
            data = cur.fetchall()
            print(data)
