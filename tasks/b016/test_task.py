from solution import initials

def test_with_fixture(db_conn):
    assert initials('grace brewster hopper') == 'GBH'
