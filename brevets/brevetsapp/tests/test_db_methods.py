from db_methods import Db

test_obj = {"ident": -300, "miles": 31, "kms": -50, "loc": "",
            "opening": "01/01/2021, 01:28 AM", "close": "01/01/2021, 03:30 AM"}


def assert_condition(condition):
    assert condition


def test_db_methods():
    db = Db()
    # db.drop_all()
    db.insert_row(test_obj)
    list_of_dicts = list(db.find_content({"kms": test_obj['kms']}))
    print("list_of_dicts:", list_of_dicts)
    assert len(list_of_dicts) == 1
    found_obj = list_of_dicts[0]
    [assert_condition(
        found_obj[val] == test_obj[val]) for val in test_obj.keys()]
    db.drop_one({'_id': found_obj['_id']})
