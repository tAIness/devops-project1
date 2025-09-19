import allure

@allure.parent_suite("Website")
@allure.suite("Homepage")
@allure.sub_suite("Smoke")
def test_py_sanity():
    assert 2 + 2 == 4

