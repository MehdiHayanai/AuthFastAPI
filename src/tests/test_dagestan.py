from scanner.dummy import send_to_dagestan


def test_send_to_dagestan() -> None:
    assert send_to_dagestan() == "Send him 2, 3 years Dagestan and forget!"
