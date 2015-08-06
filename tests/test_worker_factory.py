from bodleian.recipe.fedorainstance import FedoraWorkerFactory


def test_what_if_no_worker_for_a_version():
    worker = FedoraWorkerFactory.get_worker('1.1')
    assert worker is None

def test_what_if_no_worker_for_none_value():
    worker = FedoraWorkerFactory.get_worker(None)
    assert worker is None